from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
from utils.db import get_session
from models.persona import Persona
from .deps import get_current_user, require_plan
import httpx
from config import settings

router = APIRouter()

@router.post("/personas/{persona_id}/train", dependencies=[Depends(require_plan("basic"))])
async def train_persona_voice(persona_id: int, files: List[UploadFile] = File(...), user=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    p = await session.get(Persona, persona_id)
    if not p or p.user_id != user["user_id"]: raise HTTPException(404, "Persona not found")
    if not settings.ELEVENLABS_API_KEY: raise HTTPException(500, "Voice training not configured")
    if not files: raise HTTPException(400, "At least 1 audio file required")
    total=0; fs=[]
    for f in files:
        c = await f.read(); total += len(c)
        if total > 100*1024*1024: raise HTTPException(400,"Total file size exceeds 100MB")
        fs.append(("files", (f.filename, c, f.content_type or "audio/mpeg")))
    url = "https://api.elevenlabs.io/v1/voices/add"; headers = {"xi-api-key": settings.ELEVENLABS_API_KEY}
    data = {"name": f"{p.name}_{user['user_id']}_{persona_id}", "description": f"Custom voice for persona: {p.name}"}
    async with httpx.AsyncClient(timeout=300) as client:
        r = await client.post(url, headers=headers, data=data, files=fs)
        if r.status_code // 100 != 2: raise HTTPException(r.status_code, f"Voice training failed: {r.text}")
        result = r.json()
    voice_id = result.get("voice_id")
    if voice_id:
        p.voice_id = voice_id; p.voice_provider = "elevenlabs"
        session.add(p); await session.commit()
        return {"status":"success","voice_id":voice_id,"message":f"Voice trained for {p.name}"}
    raise HTTPException(500, "No voice_id returned from API")

@router.get("/personas/{persona_id}/voice-info")
async def get_voice_info(persona_id: int, user=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    p = await session.get(Persona, persona_id)
    if not p or p.user_id != user["user_id"]: raise HTTPException(404, "Persona not found")
    if not p.voice_id: return {"has_custom_voice": False, "provider": p.voice_provider, "message": "Using default voice."}
    return {"has_custom_voice": True, "voice_id": p.voice_id, "provider": p.voice_provider}
