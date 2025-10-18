"""
Application Settings

This module contains all configuration settings for the BFF service.
Uses Pydantic Settings for environment variable management.
"""

import os
import secrets
from functools import lru_cache
from typing import List, Optional, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    # Application Configuration
    app_name: str = Field(default="Connet.AI BFF Service", env="APP_NAME")
    app_version: str = Field(default="0.1.0", env="APP_VERSION")
    app_env: str = Field(default="development", env="APP_ENV")
    debug: bool = Field(default=True, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    reload: bool = Field(default=True, env="RELOAD")
    
    # Security Configuration
    secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Database Configuration (Supabase)
    supabase_url: Optional[str] = Field(default=None, env="SUPABASE_URL")
    supabase_anon_key: Optional[str] = Field(default=None, env="SUPABASE_ANON_KEY") 
    supabase_service_role_key: Optional[str] = Field(default=None, env="SUPABASE_SERVICE_ROLE_KEY")
    database_url: Optional[str] = Field(default="postgresql+asyncpg://postgres:password@localhost:5432/connet_ai", env="DATABASE_URL")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")
    
    # CORS Configuration - validators will convert strings to lists
    cors_origins: List[str] = Field(
        default="http://localhost:3000", 
        env="CORS_ORIGINS"
    )
    cors_methods: List[str] = Field(
        default="GET,POST,PUT,DELETE,OPTIONS",
        env="CORS_METHODS"
    )
    cors_headers: List[str] = Field(default="*", env="CORS_HEADERS")
    
    # AI Service Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_base_url: Optional[str] = Field(default=None, env="OPENAI_BASE_URL")
    openai_org_id: Optional[str] = Field(default=None, env="OPENAI_ORG_ID")
    openai_default_model: str = Field(default="gpt-4o-mini", env="OPENAI_DEFAULT_MODEL")
    
    # LangSmith Tracing Configuration
    langsmith_tracing: bool = Field(default=False, env="LANGSMITH_TRACING")
    langsmith_endpoint: str = Field(default="https://api.smith.langchain.com", env="LANGSMITH_ENDPOINT")
    langsmith_api_key: Optional[str] = Field(default=None, env="LANGSMITH_API_KEY")
    langsmith_project: str = Field(default="connet-ai-dev", env="LANGSMITH_PROJECT")
    
    # Legacy support
    langchain_tracing_v2: bool = Field(default=False, env="LANGCHAIN_TRACING_V2")
    langchain_endpoint: Optional[str] = Field(default=None, env="LANGCHAIN_ENDPOINT")
    langchain_api_key: Optional[str] = Field(default=None, env="LANGCHAIN_API_KEY")
    
    # Vector Database
    vector_dimension: int = Field(default=1536, env="VECTOR_DIMENSION")
    
    # File Storage
    storage_bucket_name: str = Field(default="connet-files", env="STORAGE_BUCKET_NAME")
    max_file_size_mb: int = Field(default=50, env="MAX_FILE_SIZE_MB")
    
    # Task Queue Configuration
    redis_queue_url: str = Field(default="redis://localhost:6379/1", env="REDIS_QUEUE_URL")
    worker_concurrency: int = Field(default=10, env="WORKER_CONCURRENCY")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_burst: int = Field(default=10, env="RATE_LIMIT_BURST")
    
    # Monitoring & Observability
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    enable_tracing: bool = Field(default=False, env="ENABLE_TRACING")
    jaeger_endpoint: Optional[str] = Field(default=None, env="JAEGER_ENDPOINT")
    
    # External Service URLs
    frontend_url: str = Field(default="http://localhost:3000", env="FRONTEND_URL")
    webhook_secret: Optional[str] = Field(default=None, env="WEBHOOK_SECRET")
    
    # Development/Testing
    test_database_url: Optional[str] = Field(default=None, env="TEST_DATABASE_URL")
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:3000"]  # fallback
    
    @field_validator("cors_methods", mode="before")
    @classmethod
    def parse_cors_methods(cls, v) -> List[str]:
        """Parse CORS methods from string or list."""
        if isinstance(v, str):
            return [method.strip() for method in v.split(",") if method.strip()]
        elif isinstance(v, list):
            return v
        return ["GET", "POST", "PUT", "DELETE", "OPTIONS"]  # fallback
    
    @field_validator("cors_headers", mode="before")
    @classmethod
    def parse_cors_headers(cls, v) -> List[str]:
        """Parse CORS headers from string or list."""
        if isinstance(v, str):
            return [header.strip() for header in v.split(",") if header.strip()]
        elif isinstance(v, list):
            return v
        return ["*"]  # fallback
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    
    @field_validator("app_env")
    @classmethod
    def validate_app_env(cls, v):
        """Validate application environment."""
        valid_envs = ["development", "staging", "production"]
        if v.lower() not in valid_envs:
            raise ValueError(f"App environment must be one of: {valid_envs}")
        return v.lower()
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env == "production"
    
    @property
    def is_staging(self) -> bool:
        """Check if running in staging mode."""
        return self.app_env == "staging"
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        # Disable automatic JSON parsing for complex types
        env_parse_none_str=None,
        env_nested_delimiter=None,
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings (cached).
    
    Environment file priority:
    1. BFF_ENV_FILE environment variable (highest priority)
    2. Environment-specific files (.env.local, .env.uat, .env.prod)
    3. Default .env file (lowest priority)
    """
    # Check for explicit env file override
    env_file = os.getenv("BFF_ENV_FILE")
    if env_file:
        return Settings(_env_file=env_file)
    
    # Check for environment-specific files
    app_env = os.getenv("APP_ENV", "development")
    env_file_map = {
        "development": ".env.local",
        "staging": ".env.uat", 
        "production": ".env.prod"
    }
    
    # Try environment-specific file first
    env_file = env_file_map.get(app_env)
    if env_file and os.path.exists(env_file):
        return Settings(_env_file=env_file)
    
    # Fall back to default .env file
    return Settings()