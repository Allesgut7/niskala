# Niskala - Cloud Configuration
# VPS deployment configuration

import os
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from typing import Optional


class CloudConfig(BaseSettings):
    """Cloud/VPS deployment configuration"""
    
    # Application
    APP_NAME: str = "Niskala"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "production"
    
    # Database (PostgreSQL)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://niskala:secret@localhost:5432/niskala")
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 5
    
    # Cache (Redis)
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_MAX_MEMORY: str = "200mb"
    
    # API
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    API_PORT: int = 8080
    API_HOST: str = "0.0.0.0"
    
    # Worker
    WORKER_CONCURRENCY: int = 2
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_BURST: int = 20
    
    # Monitoring
    ENABLE_METRICS: bool = True
    LOG_LEVEL: str = "info"
    
    # Backup
    BACKUP_ENABLED: bool = True
    BACKUP_RETENTION_DAYS: int = 7
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton instance
config = CloudConfig()


def get_config() -> CloudConfig:
    """Get configuration instance"""
    return config
