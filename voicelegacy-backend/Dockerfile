# Simple Dockerfile for Voice Legacy Backend
FROM python:3.11-slim

WORKDIR /app

# System deps needed for audio + healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt \
 # ensure email validation is present even if not in requirements.txt
 && pip install --no-cache-dir "pydantic[email]"

# App code
COPY . .

# Folders the app expects
RUN mkdir -p media/audio media/video media/avatars chroma_db

EXPOSE 8000

# Simple healthcheck (optional)
HEALTHCHECK --interval=30s --timeout=10s --start-period=25s --retries=3 \
  CMD curl -fsS http://localhost:8000/health || exit 1

# Start server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
