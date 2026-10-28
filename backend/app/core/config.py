"""
Configuration Management
Centralized configuration using environment variables with validation.
"""
import os
from typing import List, Optional
from functools import lru_cache
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Assistive AI Platform"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = Field(default="development", pattern="^(development|staging|production)$")

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    # Security
    secret_key: str = Field(default="", min_length=32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS
    allowed_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"])
    allowed_methods: List[str] = Field(default_factory=lambda: ["GET", "POST"])
    allowed_headers: List[str] = Field(default_factory=lambda: ["Authorization", "Content-Type"])

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60
    rate_limit_burst: int = 10

    # WebSocket
    ws_heartbeat_interval: int = 30
    ws_max_connections: int = 100
    ws_max_message_size: int = 10 * 1024 * 1024  # 10MB

    # Frame Validation
    max_frame_size_bytes: int = 5 * 1024 * 1024  # 5MB
    allowed_frame_formats: List[str] = Field(default_factory=lambda: ["jpeg", "jpg", "png"])
    max_frame_dimension: int = 1920

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_ssl: bool = False
    redis_default_ttl: int = 300

    # Model Paths
    yolo_model_path: str = "./app/models/yolov8n.onnx"
    ocr_languages: List[str] = Field(default_factory=lambda: ["en"])
    ocr_gpu: bool = False
    vlm_model_name: str = "Salesforce/blip-image-captioning-base"

    # TTS
    tts_rate: int = 200
    tts_volume: float = 0.9

    # Logging
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    log_format: str = "json"

    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @validator("secret_key")
    def validate_secret_key(cls, v):
        if not v or len(v) < 32:
            if os.getenv("ENVIRONMENT") == "production":
                raise ValueError("SECRET_KEY must be at least 32 characters in production")
        return v

    @validator("allowed_origins")
    def validate_origins(cls, v):
        if "*" in v and os.getenv("ENVIRONMENT") == "production":
            raise ValueError("Wildcard CORS origin not allowed in production")
        return v


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()