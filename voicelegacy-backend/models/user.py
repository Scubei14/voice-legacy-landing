from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    display_name: Optional[str] = None
    role: str = Field(default="user")
    refresh_version: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
