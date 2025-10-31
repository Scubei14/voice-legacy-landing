# Docker Quick Start

## Minimal (backend only)
cp .env.example .env
docker compose up --build -d
docker compose logs -f backend

## Full stack (Postgres + MinIO + Redis)
cp .env.example .env
docker compose -f docker-compose.full.yml up --build -d

# Health
curl http://localhost:8000/health

# MinIO console
# http://localhost:9001  (user: minioadmin / pass: minioadmin)
# Create bucket matching S3_BUCKET in .env (default: voice-legacy)

# Stop
docker compose -f docker-compose.full.yml down
