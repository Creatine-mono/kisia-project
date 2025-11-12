"""
애플리케이션 설정
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정 클래스"""
    
    # App
    APP_NAME: str = "AI-TLS-DLP Backend"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://admin:password123@localhost:5432/ai_tlsdlp"
    
    # JWT
    SECRET_KEY: str = "dlp-secret-key-change-in-production-minimum-32-characters-required"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI Model
    PII_MODEL_NAME: str = "psh3333/roberta-large-korean-pii5"
    DEFAULT_PII_THRESHOLD: float = 0.59
    MODEL_MODE: str = "LOCAL"

    # Elasticsearch
    ELASTICSEARCH_HOST: str = "localhost"
    ELASTICSEARCH_PORT: int = 9200
    ELASTICSEARCH_INDEX_PREFIX: str = "pii-detection"
    ELASTICSEARCH_LOG_RETENTION_DAYS: int = 30

    @property
    def elasticsearch_url(self) -> str:
        """Elasticsearch URL 생성"""
        return f"http://{self.ELASTICSEARCH_HOST}:{self.ELASTICSEARCH_PORT}"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
