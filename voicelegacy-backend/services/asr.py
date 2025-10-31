import httpx, tempfile, os
from config import settings

async def transcribe_bytes(audio_bytes: bytes, mime: str = 'audio/webm') -> dict:
    if not settings.OPENAI_API_KEY:
        return {'text': ''}
    url = 'https://api.openai.com/v1/audio/transcriptions'
    headers = {'Authorization': f'Bearer {settings.OPENAI_API_KEY}'}
    suffix = '.webm' if 'webm' in mime else ('.mp3' if 'mp3' in mime else '.wav')
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(audio_bytes); tmp_path = tmp.name
    try:
        data = {'model': settings.ASR_MODEL}
        with open(tmp_path, 'rb') as f:
            files = {'file': (os.path.basename(tmp_path), f, mime)}
            async with httpx.AsyncClient(timeout=120) as client:
                r = await client.post(url, headers=headers, data=data, files=files)
                r.raise_for_status()
                return r.json()
    except Exception as e:
        return {'text':'', 'error': str(e)}
    finally:
        try: os.remove(tmp_path)
        except: pass
