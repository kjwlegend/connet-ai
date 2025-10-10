"""SQLModel definitions for per-user LLM settings."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class UserLLMSettingsModel(SQLModel, table=True):
    """Large-language-model configuration per user."""

    __tablename__ = "user_llm_settings"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="users.id", unique=True, index=True)

    default_provider: str = Field(default="openai", max_length=50)
    default_model: str = Field(default="gpt-3.5-turbo", max_length=100)

    provider_configs: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))

    chat_model: Optional[str] = Field(default=None, max_length=100)
    coding_model: Optional[str] = Field(default=None, max_length=100)
    writing_model: Optional[str] = Field(default=None, max_length=100)
    analysis_model: Optional[str] = Field(default=None, max_length=100)
    creative_model: Optional[str] = Field(default=None, max_length=100)

    default_temperature: float = Field(default=0.7)
    default_max_tokens: int = Field(default=2048)
    default_top_p: float = Field(default=1.0)
    default_frequency_penalty: float = Field(default=0.0)
    default_presence_penalty: float = Field(default=0.0)

    api_keys: Dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON))

    auto_select_model: bool = Field(default=True)
    cost_optimization_enabled: bool = Field(default=True)
    quality_preference: str = Field(default="balanced", max_length=20)

    streaming_enabled: bool = Field(default=True)
    response_format_preference: str = Field(default="markdown", max_length=20)
    content_filtering_level: str = Field(default="moderate", max_length=20)
    enable_fact_checking: bool = Field(default=False)

    global_system_prompt: Optional[str] = Field(default=None)
    context_length_preference: int = Field(default=4000)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


__all__ = ["UserLLMSettingsModel"]
