"""Application configuration management."""
import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "Event Processing Microservice"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # Database
    database_url: str = "postgresql://postgres:abc123@localhost:5432/new_events_db"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # AWS Configuration
    aws_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    
    # SQS Configuration
    # sdasd: str = "http://localhost:9325/events-queue"
    # sqs_endpoint_url: Optional[str] = "http://localhost:9325"
    # sqs_max_messages: int = 10
    # sqs_wait_time_seconds: int = 20
    
    # Worker Configuration
    worker_concurrency: int = 5
    worker_poll_interval: int = 5
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Global settings instance
settings = get_settings()