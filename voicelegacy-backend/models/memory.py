from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Memory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    persona_id: Optional[int] = Field(default=None, index=True)
    text: str
    tags: Optional[str] = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
