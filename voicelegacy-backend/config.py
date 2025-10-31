from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional
import warnings

class Settings(BaseSettings):
    APP_NAME: str = "VoiceLegacyAI Backend"
    APP_DEBUG: bool = False
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    ENV: str = "prod"

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_MIN: int = 60
    JWT_REFRESH_EXPIRES_MIN: int = 43200

    DATABASE_URL: str = "sqlite+aiosqlite:///./voice_legacy.db"

    VECTOR_BACKEND: str = "chroma"
    CHROMA_DIR: str = "./chroma_db"
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_INDEX: str = "vla-memories"
    PINECONE_CLOUD: str = "aws"
    PINECONE_REGION: str = "us-east-1"

    EMBEDDINGS_MODEL: str = "all-MiniLM-L6-v2"

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    ASR_MODEL: str = "whisper-1"

    ELEVENLABS_API_KEY: Optional[str] = None
    ELEVENLABS_VOICE_ID: Optional[str] = None

    S3_ENDPOINT: Optional[str] = None
    S3_REGION: str = "us-east-1"
    S3_BUCKET: str = "voice-legacy"
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_USE_PATH_STYLE: bool = True

    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: str = "no-reply@voicelegacy.local"
    SMTP_TLS: bool = True

    CORS_ORIGINS: List[str] = ["*"]
    FRONTEND_URL: str = "http://localhost:3000"

    RATE_LIMIT_PER_MINUTE: int = 240
    MAX_RESET_REQUESTS_PER_HOUR: int = 3
    REDIS_URL: Optional[str] = None

    SENTRY_DSN: Optional[str] = None

    FEATURE_FLAGS: str = ""

    METAHUMAN_API_URL: Optional[str] = None
    METAHUMAN_API_KEY: Optional[str] = None
    SADTALKER_SERVICE_URL: Optional[str] = None

    @field_validator("JWT_SECRET")
    def jwt_secret_strength(cls, v):
        if len(v) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters")
        return v

    @field_validator("CORS_ORIGINS")
    def validate_cors(cls, v):
        if "*" in v:
            warnings.warn("CORS set to '*' - unsafe for production")
        return v

    model_config = {"env_file": ".env", "case_sensitive": False}

settings = Settings()
