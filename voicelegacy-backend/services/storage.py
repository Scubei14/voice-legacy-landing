import os, pathlib, aiofiles
from typing import Optional
from config import settings
MEDIA_ROOT = pathlib.Path("media")

async def put_bytes(key: str, data: bytes, mime: str = "application/octet-stream") -> str:
    path = MEDIA_ROOT / key
    path.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(path, "wb") as f:
        await f.write(data)
    return f"/media/{key}"
