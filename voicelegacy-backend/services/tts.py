import httpx, base64, asyncio
from config import settings

async def elevenlabs_tts(text: str, voice_id: str | None = None, settings_override: dict | None = None) -> dict:
    if not settings.ELEVENLABS_API_KEY:
        return {"provider":"elevenlabs","audio_b64": None}
    voice = voice_id or settings.ELEVENLABS_VOICE_ID or "EXAVITQu4vr4xnSDxMaL"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
    headers = {"xi-api-key": settings.ELEVENLABS_API_KEY, "accept":"audio/mpeg", "content-type":"application/json"}
    payload = {"text": text[:5000], "model_id": "eleven_multilingual_v2", "voice_settings": {"stability":0.5,"similarity_boost":0.75}}
    if settings_override: payload["voice_settings"].update({k:v for k,v in settings_override.items() if k in ("stability","similarity_boost")})
    async with httpx.AsyncClient(timeout=120) as client:
        for attempt in range(3):
            r = await client.post(url, headers=headers, json=payload)
            if r.status_code == 200:
                return {"provider":"elevenlabs","mime":"audio/mpeg","audio_b64": base64.b64encode(r.content).decode("utf-8")}
            if r.status_code == 429:
                await asyncio.sleep(2**attempt); continue
            return {"provider":"elevenlabs","error": r.text, "status": r.status_code}
    return {"provider":"elevenlabs","error":"rate limited"}
