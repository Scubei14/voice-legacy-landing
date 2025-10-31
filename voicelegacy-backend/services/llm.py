from __future__ import annotations
import httpx
from config import settings

async def openai_chat(messages: list[dict]) -> dict:
    if not settings.OPENAI_API_KEY:
        user_last = next((m for m in reversed(messages) if m.get("role")=="user"), {"content": ""})
        return {"message": f"(mocked) I hear you: {user_last.get('content','').strip()}"}
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
    payload = {"model": settings.OPENAI_MODEL, "messages": messages}
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        return {"message": data["choices"][0]["message"]["content"]}
