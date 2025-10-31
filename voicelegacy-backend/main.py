from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
from contextlib import asynccontextmanager
import uuid, os

from config import settings
from utils.db import init_db
from utils.logging import logger
from utils.metrics import MetricsMiddleware, metrics_router

from routes import auth, personas, memories, ingest, voice, analytics, historical, voice_training

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Voice Legacy AI Backend...")
    await init_db()
    try:
        from services import emotion, embeddings
        emotion.ensure(); embeddings._load()
        logger.info("✅ Models ready (or gracefully degraded)")
    except Exception as e:
        logger.warning("Model preload failed: %s", e)
    os.makedirs("media/audio", exist_ok=True)
    os.makedirs("media/video", exist_ok=True)
    os.makedirs("media/avatars", exist_ok=True)
    yield

app = FastAPI(title=settings.APP_NAME, debug=settings.APP_DEBUG, lifespan=lifespan, version="1.0.0")

app.add_middleware(MetricsMiddleware)
app.include_router(metrics_router, tags=["metrics"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if settings.ENV == "prod":
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    return JSONResponse(status_code=500, content={"detail": str(exc), "type": type(exc).__name__})

if os.path.exists("media"):
    app.mount("/media", StaticFiles(directory="media"), name="media")

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(personas.router, prefix="/api/personas", tags=["personas"])
app.include_router(memories.router, prefix="/api/memories", tags=["memories"])
app.include_router(ingest.router, prefix="/api/ingest", tags=["ingest"])
app.include_router(voice.router, prefix="/realtime/voice", tags=["realtime"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(historical.router, prefix="/api/historical", tags=["historical"])
app.include_router(voice_training.router, prefix="/api", tags=["voice-training"])

@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>Voice Legacy AI</h1><p>Docs: <a href='/docs'>/docs</a></p>"

@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.ENV, "vector_backend": settings.VECTOR_BACKEND}
