"""Schemas for the AI memory module."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    """Memory tier classification."""

    SHORT_TERM = "short_term"
    MEDIUM_TERM = "medium_term"
    LONG_TERM = "long_term"


class MemoryCategory(str, Enum):
    """Memory semantic category."""

    CONVERSATION = "conversation"
    USER_PREFERENCE = "user_preference"
    KNOWLEDGE = "knowledge"
    PATTERN = "pattern"
    ENTITY = "entity"


class MemoryCreate(BaseModel):
    """Payload for creating a memory record."""

    conversation_id: UUID
    agent_id: Optional[UUID] = Field(default=None)
    memory_type: MemoryType = Field(..., description="Memory tier")
    memory_category: MemoryCategory = Field(
        ..., description="Memory semantic category"
    )
    content: str = Field(..., min_length=1, description="Memory content")
    memory_metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Metadata for the memory"
    )
    importance_score: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Importance weighting"
    )
    confidence_score: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Confidence weighting"
    )
    emotional_valence: float = Field(
        default=0.0, ge=-1.0, le=1.0, description="Emotional valence score"
    )


class MemoryResponse(BaseModel):
    """Response representation for stored memory."""

    id: UUID
    conversation_id: UUID
    agent_id: Optional[UUID]
    memory_type: MemoryType
    memory_category: MemoryCategory
    content: str
    memory_metadata: Dict[str, Any]
    importance_score: float
    confidence_score: float
    emotional_valence: float
    created_at: datetime
    access_count: int

    class Config:
        from_attributes = True


class ConversationSummaryResponse(BaseModel):
    """Response representation for conversation summaries."""

    id: UUID
    conversation_id: UUID
    summary_text: str
    key_points: List[str]
    entities: List[Dict[str, Any]]
    topics: List[str]
    sentiment: str
    time_range_start: datetime
    time_range_end: datetime
    message_count: int
    created_at: datetime

    class Config:
        from_attributes = True


__all__ = [
    "MemoryType",
    "MemoryCategory",
    "MemoryCreate",
    "MemoryResponse",
    "ConversationSummaryResponse",
]
