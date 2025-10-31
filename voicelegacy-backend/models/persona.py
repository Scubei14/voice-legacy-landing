from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Persona(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    name: str
    voice_provider: str = "elevenlabs"
    voice_id: Optional[str] = None
    traits_json: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
