from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from utils.db import get_session
from models.persona import Persona
from .deps import get_current_user
import json

router = APIRouter()
VOICE_PROVIDERS = {"elevenlabs"}

class PersonaIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    voice_provider: str = Field(default="elevenlabs")
    voice_id: Optional[str] = None
    traits: Dict[str, Any] = Field(default_factory=dict)

class PersonaOut(BaseModel):
    id: int
    name: str
    voice_provider: str
    voice_id: Optional[str]
    traits: Dict[str, Any]
    created_at: str

class PersonaListOut(BaseModel):
    total: int
    items: List[PersonaOut]

def _to_out(p: Persona) -> PersonaOut:
    return PersonaOut(id=p.id, name=p.name, voice_provider=p.voice_provider, voice_id=p.voice_id, traits=json.loads(p.traits_json or "{}"), created_at=p.created_at.isoformat())

@router.get("/", response_model=PersonaListOut)
async def list_personas(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0), user=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    res = await session.exec(select(Persona).where(Persona.user_id == user["user_id"]).order_by(Persona.created_at.desc()))
    all_p = res.all()
    items = [_to_out(p).model_dump() for p in all_p[offset:offset+limit]]
    return {"total": len(all_p), "items": items}

@router.post("/", response_model=PersonaOut)
async def create_persona(data: PersonaIn, user=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    if data.voice_provider not in VOICE_PROVIDERS: raise HTTPException(422, "Unsupported voice provider")
    p = Persona(user_id=user["user_id"], name=data.name.strip(), voice_provider=data.voice_provider, voice_id=data.voice_id, traits_json=json.dumps(data.traits, ensure_ascii=False))
    session.add(p); await session.commit(); await session.refresh(p)
    return _to_out(p)

@router.get("/{persona_id}", response_model=PersonaOut)
async def get_persona(persona_id: int, user=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    p = await session.get(Persona, persona_id)
    if not p or p.user_id != user["user_id"]:
        raise HTTPException(404, "Persona not found")
    return _to_out(p)

@router.patch("/{persona_id}", response_model=PersonaOut)
async def update_persona(persona_id: int, data: PersonaIn, user=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    p = await session.get(Persona, persona_id)
    if not p or p.user_id != user["user_id"]:
        raise HTTPException(404, "Persona not found")
    if data.voice_provider not in VOICE_PROVIDERS:
        raise HTTPException(422, "Unsupported voice provider")
    p.name = data.name.strip(); p.voice_provider = data.voice_provider; p.voice_id = data.voice_id; p.traits_json = json.dumps(data.traits, ensure_ascii=False)
    session.add(p); await session.commit(); await session.refresh(p)
    return _to_out(p)

@router.delete("/{persona_id}")
async def delete_persona(persona_id: int, user=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    p = await session.get(Persona, persona_id)
    if not p or p.user_id != user["user_id"]:
        raise HTTPException(404, "Persona not found")
    await session.delete(p); await session.commit()
    return {"status": "deleted", "persona_id": persona_id}
