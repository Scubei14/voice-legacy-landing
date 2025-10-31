from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import settings

_async_engine = None
Session = None

async def init_db():
    global _async_engine, Session
    _async_engine = create_async_engine(settings.DATABASE_URL, future=True, echo=False)
    async with _async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    Session = sessionmaker(_async_engine, class_=AsyncSession, expire_on_commit=False)

async def get_session():
    async with Session() as s:
        yield s
