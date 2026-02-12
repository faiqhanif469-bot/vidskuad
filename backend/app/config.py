"""
Configuration Settings
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    APP_NAME: str = "AI Video Production"
    DEBUG: bool = False
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://vidsquad.vercel.app",
        "https://*.vercel.app",
        "*"  # Allow all for now
    ]
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # 1 hour
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "")
    
    # DigitalOcean Spaces
    DO_SPACES_KEY: str = os.getenv("DO_SPACES_KEY", "")
    DO_SPACES_SECRET: str = os.getenv("DO_SPACES_SECRET", "")
    DO_SPACES_REGION: str = os.getenv("DO_SPACES_REGION", "nyc3")
    DO_SPACES_BUCKET: str = os.getenv("DO_SPACES_BUCKET", "ai-video-production")
    DO_SPACES_ENDPOINT: str = f"https://{DO_SPACES_REGION}.digitaloceanspaces.com"
    
    # File cleanup
    FILE_RETENTION_MINUTES: int = 20  # Auto-delete after 20 minutes
    
    # Rate limiting
    RATE_LIMIT_FREE: int = 5  # 5 videos per month
    RATE_LIMIT_PRO: int = 50  # 50 videos per month
    RATE_LIMIT_ENTERPRISE: int = 999999  # Unlimited
    
    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    CLOUDFLARE_ACCOUNT_ID: str = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
    CLOUDFLARE_API_TOKEN: str = os.getenv("CLOUDFLARE_API_TOKEN", "")
    
    # Job settings
    MAX_CONCURRENT_JOBS: int = 4  # Max 4 videos processing at once
    JOB_TIMEOUT_MINUTES: int = 30  # Job timeout
    
    # Storage settings
    USE_LOCAL_STORAGE: bool = False
    LOCAL_STORAGE_PATH: str = "/app/output"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env


settings = Settings()
