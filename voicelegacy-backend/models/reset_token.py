from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class ResetToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    token: str = Field(index=True, unique=True)
    used: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
