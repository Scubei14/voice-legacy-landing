import time
from fastapi import HTTPException
from config import settings

BUCKET = {}

async def rate_limit(key: str):
    now = int(time.time())
    bucket = BUCKET.setdefault(now, {})
    prev = bucket.get(key, 0)
    if prev >= settings.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(429, "Rate limit exceeded")
    bucket[key] = prev + 1
    old = [sec for sec in BUCKET.keys() if sec < now]
    for sec in old: BUCKET.pop(sec, None)
