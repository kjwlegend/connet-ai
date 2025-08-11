"""
User LLM Settings Database Model

This module defines the SQLModel for user's LLM model preferences and settings.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class UserLLMSettingsModel(SQLModel, table=True):
    """User LLM settings database model."""
    
    __tablename__ = "user_llm_settings"
    
    # Primary key
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique settings identifier"
    )
    user_id: UUID = Field(
        foreign_key="users.id",
        index=True,
        unique=True,
        description="User ID (one settings per user)"
    )
    
    # Default model selection
    default_provider: str = Field(
        default="openai",
        max_length=50,
        description="Default LLM provider: openai, anthropic, google, cohere, etc."
    )
    default_model: str = Field(
        default="gpt-3.5-turbo",
        max_length=100,
        description="Default model name"
    )
    
    # Provider configurations
    provider_configs: Dict[str, Any] = Field(
        default={},
        description="Per-provider configuration settings"
    )
    
    # Model preferences by use case
    chat_model: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Preferred model for casual chat"
    )
    coding_model: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Preferred model for coding tasks"
    )
    writing_model: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Preferred model for writing tasks"
    )
    analysis_model: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Preferred model for analysis tasks"
    )
    creative_model: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Preferred model for creative tasks"
    )
    
    # Default parameters
    default_temperature: float = Field(
        default=0.7,
        description="Default temperature setting (0.0-2.0)"
    )
    default_max_tokens: int = Field(
        default=2048,
        description="Default maximum tokens"
    )
    default_top_p: float = Field(
        default=1.0,
        description="Default top-p setting (0.0-1.0)"
    )
    default_frequency_penalty: float = Field(
        default=0.0,
        description="Default frequency penalty (0.0-2.0)"
    )
    default_presence_penalty: float = Field(
        default=0.0,
        description="Default presence penalty (0.0-2.0)"
    )
    
    # API keys and authentication (encrypted)
    api_keys: Dict[str, str] = Field(
        default={},
        description="Encrypted API keys for different providers"
    )
    
    # Usage preferences
    auto_select_model: bool = Field(
        default=True,
        description="Whether to auto-select best model for task type"
    )
    cost_optimization_enabled: bool = Field(
        default=True,
        description="Whether to optimize for cost when selecting models"
    )
    quality_preference: str = Field(
        default="balanced",
        max_length=20,
        description="Quality preference: fast, balanced, high_quality"
    )
    
    # Response preferences
    streaming_enabled: bool = Field(
        default=True,
        description="Whether to enable streaming responses"
    )
    response_format_preference: str = Field(
        default="markdown",
        max_length=20,
        description="Preferred response format: plain, markdown, json"
    )
    
    # Safety and moderation
    content_filtering_level: str = Field(
        default="moderate",
        max_length=20,
        description="Content filtering level: strict, moderate, permissive"
    )
    enable_fact_checking: bool = Field(
        default=False,
        description="Whether to enable fact-checking for responses"
    )
    
    # Custom system prompts
    global_system_prompt: Optional[str] = Field(
        default=None,
        description="Global system prompt to prepend to all requests"
    )
    context_length_preference: int = Field(
        default=4000,
        description="Preferred context length for conversations"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Settings creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    class Config:
        """SQLModel configuration."""
        schema_extra = {
            "example": {
                "user_id": "12345678-1234-5678-9012-123456789012",
                "default_provider": "openai",
                "default_model": "gpt-4",
                "provider_configs": {
                    "openai": {
                        "organization_id": "org-123456",
                        "rate_limit_per_minute": 60
                    },
                    "anthropic": {
                        "rate_limit_per_minute": 50
                    }
                },
                "chat_model": "gpt-3.5-turbo",
                "coding_model": "gpt-4",
                "writing_model": "claude-3-sonnet",
                "analysis_model": "gpt-4",
                "creative_model": "claude-3-opus",
                "default_temperature": 0.8,
                "default_max_tokens": 2048,
                "auto_select_model": True,
                "cost_optimization_enabled": True,
                "quality_preference": "balanced",
                "streaming_enabled": True,
                "response_format_preference": "markdown",
                "content_filtering_level": "moderate",
                "context_length_preference": 8000
            }
        }