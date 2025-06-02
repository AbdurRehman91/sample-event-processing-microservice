"""Application configuration management."""
import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "Event Processing Microservice"
    app_description: str = "A microservice for processing application usage events with AWS SQS and RDS."
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # Database
    # Default database URL, can be overridden by environment variable
    database_url: str = os.getenv("DATABASE_URL")
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # AWS Configuration
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    # SQS Configuration
    elasticmq_endpoint_url: Optional[str] = os.getenv("ELASTICMQ_ENDPOINT_URL")
    sqs_max_messages: int = 10
    sqs_wait_time_seconds: int = 20
    
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