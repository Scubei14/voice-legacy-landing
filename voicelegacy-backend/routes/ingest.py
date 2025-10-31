from fastapi import APIRouter, UploadFile, File, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from utils.db import get_session
from .deps import get_current_user, require_plan
from services import storage, asr, emotion, vector_store
from models.memory import Memory

router = APIRouter()

@router.post('/transcribe', dependencies=[Depends(require_plan('basic'))])
async def transcribe(file: UploadFile = File(...), user=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    data = await file.read()
    key = f"users/{user['user_id']}/media/{file.filename}"
    url = await storage.put_bytes(key, data, mime=file.content_type or 'application/octet-stream')
    tx = await asr.transcribe_bytes(data, mime=file.content_type or 'audio/webm')
    text = (tx.get('text') or '').strip()
    em = emotion.top_emotions(text) if text else [{'label': 'neutral', 'score': 0.5}]
    top_emotion = em[0]['label'] if em else 'unknown'
    m = Memory(user_id=user['user_id'], text=text, tags=f'ingest,transcript,emotion:{top_emotion}')
    session.add(m); await session.commit(); await session.refresh(m)
    try: vector_store.add(str(m.id), text, user['user_id'], None)
    except Exception: pass
    return {'memory_id': m.id, 'text': text, 'emotions': em, 'media_key': key, 'media_url': url, 'transcription': tx}
