"""Models for AI memory and summaries."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

class AIMemoryModel(SQLModel, table=True):
    """AI Memory storage model for three-tier memory system"""

    __tablename__ = "ai_memories"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    agent_id: Optional[UUID] = Field(foreign_key="agents.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)

    # Memory classification
    memory_type: str = Field(max_length=50)  # short_term, medium_term, long_term
    memory_category: str = Field(
        max_length=100
    )  # conversation, user_preference, knowledge, pattern

    # Memory content
    content: str = Field(sa_column=Column(Text))
    agent_metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    context: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))

    # Memory attributes
    importance_score: float = Field(default=0.5)  # 0.0 to 1.0
    confidence_score: float = Field(default=1.0)  # 0.0 to 1.0
    emotional_valence: float = Field(default=0.0)  # -1.0 to 1.0

    # Lifecycle management
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None)
    last_accessed_at: datetime = Field(default_factory=datetime.utcnow)
    access_count: int = Field(default=0)

    # Embedding for semantic search
    embedding_model: Optional[str] = Field(default=None, max_length=100)
    # Note: actual embedding vectors will be stored in a separate table or vector database


class AIConversationSummaryModel(SQLModel, table=True):
    """AI conversation summary for medium-term memory"""

    __tablename__ = "ai_conversation_summaries"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    agent_id: Optional[UUID] = Field(foreign_key="agents.id", index=True)

    # Summary content
    summary_text: str = Field(sa_column=Column(Text))
    key_points: List[str] = Field(default=[], sa_column=Column(JSONB))
    entities: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSONB))
    topics: List[str] = Field(default=[], sa_column=Column(JSONB))
    sentiment: str = Field(default="neutral", max_length=50)

    # Context information
    time_range_start: datetime
    time_range_end: datetime
    message_count: int = Field(default=0)
    participant_count: int = Field(default=0)

    # Quality metrics
    summary_quality_score: float = Field(default=1.0)
    completeness_score: float = Field(default=1.0)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = Field(default=None)
    is_processed: bool = Field(default=False)
