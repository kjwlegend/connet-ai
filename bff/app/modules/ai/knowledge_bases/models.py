"""Models for AI knowledge bases and documents."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, JSON, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class KnowledgeBaseModel(SQLModel, table=True):
    """Stores knowledge bases that can be attached to agents."""

    __tablename__ = "knowledge_database"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(sa_column=Column("name", Text, nullable=False, unique=True))
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    knowledge_type: str = Field(max_length=100)
    owner_id: Optional[UUID] = Field(default=None, foreign_key="users.id")

    document_ids: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    rag_config: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    is_active: bool = Field(default=True)

    metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    knowledge_metadata: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[UUID] = Field(default=None, foreign_key="users.id")


class KnowledgeDocumentModel(SQLModel, table=True):
    """Documents stored inside a knowledge base."""

    __tablename__ = "knowledge_document"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    knowledge_base_id: UUID = Field(foreign_key="knowledge_database.id", nullable=False)
    title: str = Field(sa_column=Column("title", Text, nullable=False))
    content: Optional[str] = Field(default=None, sa_column=Column(Text))
    knowledge_document_metadata: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    is_active: bool = Field(default=True)

    class Config:
        from_attributes = True


__all__ = ["KnowledgeBaseModel", "KnowledgeDocumentModel"]
