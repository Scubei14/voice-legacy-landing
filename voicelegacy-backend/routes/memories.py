from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlmodel.ext.asyncio.session import AsyncSession
from utils.db import get_session
from .deps import get_current_user
from models.memory import Memory
from services import vector_store

router = APIRouter()

class MemoryIn(BaseModel):
    text: str
    tags: Optional[str] = ""

@router.post("/", response_model=Dict[str, Any])
async def create_memory(data: MemoryIn, user=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    m = Memory(user_id=user["user_id"], text=data.text, tags=data.tags or "")
    session.add(m); await session.commit(); await session.refresh(m)
    try: vector_store.add(str(m.id), data.text, user["user_id"], None)
    except Exception: pass
    return {"id": m.id, "text": m.text, "tags": m.tags, "created_at": m.created_at.isoformat()}

class SearchIn(BaseModel):
    query: str
    top_k: int = 5

@router.post("/search", response_model=Dict[str, Any])
async def search_memories(data: SearchIn, user=Depends(get_current_user)):
    hits = vector_store.query(data.query, user_id=user["user_id"], top_k=data.top_k)
    return {"results": hits}
