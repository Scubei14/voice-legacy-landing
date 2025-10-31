from fastapi import Depends, HTTPException, Request
from sqlmodel.ext.asyncio.session import AsyncSession
from utils.security import decode_token
from utils.db import get_session
from utils.ratelimit import rate_limit as _rate_limit

async def get_current_user(request: Request, session: AsyncSession = Depends(get_session)):
    auth = request.headers.get("Authorization","")
    token = auth.split("Bearer ")[-1].strip() if "Bearer " in auth else None
    if not token: raise HTTPException(401, "Missing bearer token")
    payload = decode_token(token)
    if not payload or "sub" not in payload: raise HTTPException(401, "Invalid token")
    return {"user_id": int(payload["sub"]), "role": payload.get("role","user")}

def require_plan(plan: str):
    async def _f(): return True
    return _f

async def require_admin(user=Depends(get_current_user)):
    if user["role"] != "admin": raise HTTPException(403, "Admin only")
    return user

async def rate_limit(request: Request):
    key = request.client.host if request.client else "local"; await _rate_limit(key)
