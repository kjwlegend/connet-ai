"""Schemas for the user prompt library slice."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import Field

from app.core.schemas import BaseSchema


class UserPromptLibraryBase(BaseSchema):
    """Shared attributes for user prompts."""

    title: str = Field(..., max_length=200, description="Prompt title")
    description: Optional[str] = Field(
        None, max_length=500, description="Prompt description"
    )
    prompt_text: str = Field(..., description="Prompt content")
    category: str = Field(
        default="general", max_length=50, description="Prompt category"
    )
    tags: List[str] = Field(default_factory=list, description="Prompt tags")
    variables: List[Dict[str, str]] = Field(
        default_factory=list, description="Structured variable definitions"
    )
    preferred_models: List[str] = Field(
        default_factory=list, description="Preferred LLMs for this prompt"
    )
    temperature: Optional[float] = Field(
        default=None, ge=0.0, le=2.0, description="Override temperature"
    )
    max_tokens: Optional[int] = Field(
        default=None, gt=0, description="Override max tokens"
    )


class UserPromptLibraryCreate(UserPromptLibraryBase):
    """Payload for creating a custom prompt."""

    is_public: bool = Field(False, description="Whether the prompt is public")
    is_favorite: bool = Field(False, description="Marks the prompt as a favorite")


class UserPromptLibraryUpdate(BaseSchema):
    """Payload for updating a custom prompt."""

    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    prompt_text: Optional[str] = Field(None)
    category: Optional[str] = Field(None, max_length=50)
    tags: Optional[List[str]] = Field(None)
    variables: Optional[List[Dict[str, str]]] = Field(None)
    preferred_models: Optional[List[str]] = Field(None)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, gt=0)
    is_public: Optional[bool] = None
    is_favorite: Optional[bool] = None


class UserPromptLibraryResponse(UserPromptLibraryBase):
    """Response model for custom prompts."""

    id: UUID
    user_id: UUID
    use_count: int = 0
    last_used_at: Optional[datetime] = None
    is_public: bool = False
    is_favorite: bool = False
    created_at: datetime
    updated_at: datetime


__all__ = [
    "UserPromptLibraryCreate",
    "UserPromptLibraryUpdate",
    "UserPromptLibraryResponse",
]
