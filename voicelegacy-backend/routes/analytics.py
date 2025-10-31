from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func
from utils.db import get_session
from models.memory import Memory
from models.persona import Persona
from .deps import get_current_user
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/personas/{persona_id}/stats")
async def persona_stats(persona_id: int, user=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    p = await session.get(Persona, persona_id)
    if not p or p.user_id != user["user_id"]:
        raise HTTPException(404, "Persona not found")
    total_result = await session.exec(select(func.count(Memory.id)).where(Memory.user_id==user["user_id"], Memory.persona_id==persona_id))
    total_memories = total_result.one()
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_result = await session.exec(select(func.count(Memory.id)).where(Memory.user_id==user["user_id"], Memory.persona_id==persona_id, Memory.created_at>=week_ago))
    recent_memories = recent_result.one()
    memories_result = await session.exec(select(Memory).where(Memory.user_id==user["user_id"], Memory.persona_id==persona_id).order_by(Memory.created_at.desc()).limit(100))
    memories = memories_result.all()
    emotion_counts = {}
    for m in memories:
        for tag in (m.tags or "").split(","):
            if tag.startswith("emotion:"):
                emotion = tag.split(":")[1]; emotion_counts[emotion] = emotion_counts.get(emotion, 0)+1
    return {"persona_id": persona_id, "persona_name": p.name, "total_memories": total_memories, "memories_last_7_days": recent_memories,
            "emotion_distribution": emotion_counts, "first_interaction": p.created_at.isoformat(),
            "last_interaction": memories[0].created_at.isoformat() if memories else None}

@router.get("/dashboard")
async def dashboard(user=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    personas_result = await session.exec(select(func.count(Persona.id)).where(Persona.user_id==user["user_id"]))
    total_personas = personas_result.one()
    memories_result = await session.exec(select(func.count(Memory.id)).where(Memory.user_id==user["user_id"]))
    total_memories = memories_result.one()
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_result = await session.exec(select(func.count(Memory.id)).where(Memory.user_id==user["user_id"], Memory.created_at>=week_ago))
    recent_activity = recent_result.one()
    return {"total_personas": total_personas, "total_memories": total_memories, "memories_last_7_days": recent_activity}
