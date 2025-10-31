from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from utils.db import get_session
from models.persona import Persona
from .deps import require_admin
from services import llm
import json

router = APIRouter()

class HistoricalPersonaIn(BaseModel):
    name: str
    era: str
    bio: str
    voice_id: str | None = None
    metahuman_asset_id: str | None = None
    sadtalker_model_id: str | None = None
    traits: dict = {}
    is_public: bool = True

@router.post("/", dependencies=[Depends(require_admin)])
async def create_historical_persona(data: HistoricalPersonaIn, session: AsyncSession = Depends(get_session)):
    p = Persona(user_id=0, name=data.name, voice_provider="elevenlabs", voice_id=data.voice_id,
                traits_json=json.dumps({**data.traits, "era": data.era, "bio": data.bio, "is_historical": True, "is_public": data.is_public,
                                        "metahuman_asset_id": data.metahuman_asset_id, "sadtalker_model_id": data.sadtalker_model_id}))
    session.add(p); await session.commit(); await session.refresh(p)
    return {"id": p.id, "name": p.name, "era": data.era, "created_at": p.created_at.isoformat()}

@router.get("/")
async def list_historical(session: AsyncSession = Depends(get_session)):
    res = await session.exec(select(Persona).where(Persona.user_id==0))
    personas = res.all()
    return [{"id": p.id, "name": p.name, "traits": json.loads(p.traits_json or "{}"), "created_at": p.created_at.isoformat()} for p in personas]

class HistoricalQueryIn(BaseModel):
    question: str
    context: str | None = None

@router.post("/{persona_id}/ask")
async def ask_historical_figure(
    persona_id: int,
    data: HistoricalQueryIn,
    session: AsyncSession = Depends(get_session)
):
    """
    Public API: Ask a question to a historical figure.
    Perfect for museum kiosks and AR experiences.
    """
    p = await session.get(Persona, persona_id)

    if not p or p.user_id != 0:
        raise HTTPException(404, "Historical persona not found")

    traits = json.loads(p.traits_json or "{}")

    # Build context-aware prompt (triple-quoted f-string; no stray quotes)
    system_prompt = f"""You are {p.name}, a historical figure from {traits.get('era', 'the past')}.

Bio: {traits.get('bio', 'No bio available')}

Respond in first person as this historical figure. Stay in character. Be historically accurate but engaging.
If asked about events after your time, acknowledge you don't have knowledge of those events."""
    # Compose messages in a normal Python list (no triple-quoted list literals)
    messages = [
        {"role": "system", "content": system_prompt}
    ]

    if data.context:
        messages.append({
            "role": "system",
            "content": f"Current location/context: {data.context}"
        })

    messages.append({"role": "user", "content": data.question})

    try:
        response = await llm.openai_chat(messages)
        return {
            "persona": p.name,
            "question": data.question,
            "answer": response.get("message", "I cannot answer that right now."),
            "era": traits.get("era")
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to generate response: {str(e)}")
