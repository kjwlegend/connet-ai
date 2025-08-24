"""
Conversation Memory Database Model

This module defines the SQLModel for conversation memories in the database.
Used for storing contextual memory during conversations.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Column, Text
from sqlalchemy import Column, JSON
from sqlalchemy.dialects.postgresql import JSONB


class ConversationMemoryModel(SQLModel, table=True):
    """Conversation memory database model for storing contextual memories."""
    
    __tablename__ = "conversation_memories"
    
    # Identity
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique memory identifier"
    )
    
    # Conversation context
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        index=True,
        description="Associated conversation ID"
    )
    participant_id: Optional[UUID] = Field(
        default=None,
        index=True,
        description="Participant ID (user or agent) who created the memory"
    )
    participant_type: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Participant type: user or agent"
    )
    
    # Memory classification
    memory_type: str = Field(
        max_length=50,
        index=True,
        description="Memory type: short_term, medium_term, long_term, contextual"
    )
    memory_category: str = Field(
        max_length=100,
        description="Memory category: user_preference, decision, fact, emotion, pattern"
    )
    
    # Memory content
    content: str = Field(
        sa_column=Column(Text),
        description="Memory content text"
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB),
        description="Contextual information and metadata"
    )
    
    # Memory attributes
    importance_score: float = Field(
        default=0.5,
        index=True,
        description="Importance score 0.0-1.0"
    )
    confidence_score: float = Field(
        default=1.0,
        description="Confidence score 0.0-1.0"
    )
    emotional_valence: float = Field(
        default=0.0,
        description="Emotional valence -1.0 to 1.0"
    )
    
    # Lifecycle management
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Memory creation timestamp"
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Memory expiration timestamp"
    )
    last_accessed_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last access timestamp"
    )
    access_count: int = Field(
        default=0,
        description="Number of times this memory has been accessed"
    )
    
    # Embedding information
    embedding_model: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Model used for generating embeddings"
    )
    
    # Additional metadata
    memory_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB),
        description="Additional memory metadata"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "conversation_id": "12345678-1234-5678-9012-123456789012",
                "participant_id": "87654321-4321-8765-2109-876543210987",
                "participant_type": "user",
                "memory_type": "short_term",
                "memory_category": "user_preference",
                "content": "User prefers concise technical explanations",
                "context": {
                    "topic": "code_review",
                    "trigger_message_id": "abcd-efgh-ijkl-mnop",
                    "conversation_turn": 3
                },
                "importance_score": 0.8,
                "confidence_score": 0.9,
                "emotional_valence": 0.1,
                "embedding_model": "text-embedding-ada-002",
                "memory_metadata": {
                    "source": "explicit_statement",
                    "extracted_by": "contact_instance_manager"
                }
            }
        }
    }