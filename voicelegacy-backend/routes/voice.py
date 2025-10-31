from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from urllib.parse import parse_qs
from utils.db import Session as _Session
from utils.security import decode_token
from services import asr, emotion, llm, tts, vector_store, grounding, style
from models.memory import Memory
from models.persona import Persona
import base64, json, asyncio

router = APIRouter()

MAX_BUFFER_SIZE = 10 * 1024 * 1024
MAX_HISTORY = 20
WEBSOCKET_TIMEOUT = 300

async def save_memory(text: str, user_id: int, persona_id, speaker: str):
    async with _Session() as session:
        m = Memory(user_id=user_id, text=text, persona_id=persona_id, tags=f'dialog,persona:{persona_id},speaker:{speaker}')
        session.add(m); await session.commit(); await session.refresh(m)
        try: vector_store.add(str(m.id), text, user_id, persona_id)
        except Exception: pass

@router.websocket('/ws')
async def voice_ws(ws: WebSocket):
    token = None
    if ws.scope.get("query_string"):
        try:
            qs = parse_qs(ws.scope["query_string"].decode("utf-8"))
            token = (qs.get("token") or [None])[0]
        except Exception:
            token = None
    user_id = 0
    if token:
        data = decode_token(token)
        if data and "sub" in data:
            try: user_id = int(data["sub"])
            except: user_id = 0
    if user_id == 0:
        await ws.close(code=1008, reason="Authentication required"); return
    await ws.accept()
    buffer = bytearray(); persona_id = None; persona_voice_id = None; persona_traits = "{}"; history = []
    try:
        while True:
            try:
                msg = await asyncio.wait_for(ws.receive_text(), timeout=WEBSOCKET_TIMEOUT)
            except asyncio.TimeoutError:
                await ws.send_text(json.dumps({'type':'timeout','message':'Connection idle for 5 minutes. Please reconnect.'})); break
            data = json.loads(msg); msg_type = data.get('type')
            if msg_type == 'start':
                persona_id = data.get('persona_id'); buffer = bytearray(); history = []
                async with _Session() as session:
                    p = await session.get(Persona, int(persona_id)) if persona_id else None
                    if p and (p.user_id == user_id or p.user_id == 0):
                        persona_voice_id = p.voice_id; persona_traits = p.traits_json or "{}"
                    elif p:
                        await ws.send_text(json.dumps({'type':'error','message':'Permission denied: not your persona'})); continue
                await ws.send_text(json.dumps({'type':'ok','message':'Conversation started','persona_id': persona_id}))
            elif msg_type == 'audio':
                try:
                    chunk = base64.b64decode(data.get('data_b64',''))
                    if len(buffer)+len(chunk) > MAX_BUFFER_SIZE:
                        await ws.send_text(json.dumps({'type':'error','message':'Audio buffer exceeded 10MB. Please commit or restart.'})); buffer = bytearray()
                    else:
                        buffer.extend(chunk)
                except Exception:
                    await ws.send_text(json.dumps({'type':'error','stage':'audio_decode','message':'Failed to decode audio chunk'}))
            elif msg_type == 'commit':
                if len(buffer) == 0:
                    await ws.send_text(json.dumps({'type':'error','message':'No audio data to process'})); continue
                mime = data.get('mime','audio/webm')
                try:
                    tx = await asr.transcribe_bytes(bytes(buffer), mime=mime); text = (tx.get('text') or '').strip()
                except Exception:
                    text = ""
                try:
                    emos = emotion.top_emotions(text) if text else [{'label':'neutral','score':0.5}]
                except Exception:
                    emos = [{'label':'neutral','score':0.5}]
                if text:
                    history.append({'role':'user','content': text}); history = history[-MAX_HISTORY:]
                    asyncio.create_task(save_memory(text, user_id, persona_id, 'user'))
                try:
                    hits = vector_store.query(text, user_id=user_id, persona_id=persona_id, top_k=5) if text else []
                except Exception:
                    hits = []
                try:
                    traits = json.loads(persona_traits or "{}")
                except Exception:
                    traits = {}
                messages = grounding.build_messages(traits, history, text, hits, emos)
                reply = f"I heard: {text or '(no speech)'}"
                try:
                    ans = await llm.openai_chat(messages); reply = ans.get('message') or reply
                except Exception: pass
                history.append({'role':'assistant','content': reply}); history = history[-MAX_HISTORY:]
                asyncio.create_task(save_memory(reply, user_id, persona_id, 'assistant'))
                try:
                    tts_settings = style.pick_tts_settings(traits, emos)
                    audio = await tts.elevenlabs_tts(reply, persona_voice_id, settings_override=tts_settings)
                except Exception:
                    audio = {'audio_b64': None}
                await ws.send_text(json.dumps({'type':'reply','text': reply, 'audio_b64': audio.get('audio_b64'), 'emotions': emos, 'user_text': text}))
                buffer = bytearray()
            elif msg_type == 'stop':
                await ws.send_text(json.dumps({'type':'ok','message':'Conversation ended'})); break
    except WebSocketDisconnect:
        pass
    except Exception:
        try: await ws.send_text(json.dumps({'type':'error','message':'Unexpected error occurred'}))
        except: pass
