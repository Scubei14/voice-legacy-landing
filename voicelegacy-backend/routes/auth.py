from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
import re
from utils.db import get_session
from models.user import User
from utils.security import hash_password, verify_password, create_token
from config import settings

router = APIRouter()

class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    display_name: str | None = None

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain an uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain a lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain a number')
        return v

class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

@router.post("/register", response_model=TokenOut)
async def register(
    data: RegisterIn,
    session: AsyncSession = Depends(get_session),
):
    # CHECK IF USER EXISTS
    result = await session.execute(
        select(User).where(User.email == data.email)
    )
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # CREATE USER
    user = User(
        email=data.email,
        display_name=data.display_name or data.email.split("@")[0],
        password_hash=hash_password(data.password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    # ISSUE TOKENS
    access = create_token(
        {
            "sub": str(user.id),
            "role": user.role,
            "rv": user.refresh_version,
        },
        minutes=settings.JWT_EXPIRES_MIN,
    )
    refresh = create_token(
        {
            "sub": str(user.id),
            "rv": user.refresh_version,
        },
        minutes=settings.JWT_REFRESH_EXPIRES_MIN,
    )

    return TokenOut(
        access_token=access,
        refresh_token=refresh,
    )

class LoginIn(BaseModel):
    email: EmailStr
    password: str

@router.post("/login", response_model=TokenOut)
async def login(
    data: LoginIn,
    session: AsyncSession = Depends(get_session),
):
    # LOOK UP USER
    result = await session.execute(
        select(User).where(User.email == data.email)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # VERIFY PASSWORD
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # ISSUE TOKENS
    access = create_token(
        {
            "sub": str(user.id),
            "role": user.role,
            "rv": user.refresh_version,
        },
        minutes=settings.JWT_EXPIRES_MIN,
    )
    refresh = create_token(
        {
            "sub": str(user.id),
            "rv": user.refresh_version,
        },
        minutes=settings.JWT_REFRESH_EXPIRES_MIN,
    )

    return TokenOut(
        access_token=access,
        refresh_token=refresh,
    )
