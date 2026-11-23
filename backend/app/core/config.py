"""
ClipGod Configuration
Centralized settings using Pydantic Settings
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App
    APP_NAME: str = "ClipGod"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    CLIPS_DIR: Path = UPLOAD_DIR / "clips"
    TEMP_DIR: Path = UPLOAD_DIR / "temp"
    
    # Database
    DATABASE_URL: str = "sqlite:///./clipgod.db"
    
    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Whisper
    WHISPER_MODEL: str = "base"
    WHISPER_DEVICE: str = "cpu"  # or "cuda"
    
    # yt-dlp
    YTDLP_FORMAT: str = "bestaudio/best"
    
    # FFmpeg
    FFMPEG_PATH: str = "ffmpeg"
    
    # API
    API_V1_PREFIX: str = "/api"
    CORS_ORIGINS: list = ["*"]
    
    # File limits
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500MB

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env


settings = Settings()

# Ensure directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.CLIPS_DIR.mkdir(parents=True, exist_ok=True)
settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)