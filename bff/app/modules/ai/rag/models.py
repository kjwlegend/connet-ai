"""Models for RAG documents and chunks."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class RAGDocumentModel(SQLModel, table=True):
    """Represents a processed document used for retrieval augmented generation."""

    __tablename__ = "rag_documents"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255)
    file_path: Optional[str] = Field(default=None, max_length=1000)
    file_type: str = Field(max_length=100)
    file_size: int = Field(default=0)

    content: str = Field(sa_column=Column(Text))
    agent_metadata: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))

    processing_status: str = Field(default="pending", max_length=50)
    chunk_count: int = Field(default=0)
    quality_score: float = Field(default=1.0)

    owner_id: UUID = Field(foreign_key="users.id")
    visibility: str = Field(default="private", max_length=50)
    shared_with: List[UUID] = Field(default_factory=list, sa_column=Column(JSONB))

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = Field(default=None)
    @classmethod
    def from_create_payload(cls, payload, owner_id: UUID) -> "RAGDocumentModel":
        return cls(
            name=payload.name,
            file_path=payload.file_path,
            file_type=payload.file_type,
            file_size=payload.file_size,
            content=payload.content,
            agent_metadata=payload.agent_metadata or {},
            owner_id=owner_id,
            visibility=payload.visibility or "private",
            shared_with=payload.shared_with or [],
        )



class RAGDocumentChunkModel(SQLModel, table=True):
    """Individual chunk of a RAG document."""

    __tablename__ = "rag_document_chunks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    document_id: UUID = Field(foreign_key="rag_documents.id", index=True)
    chunk_index: int = Field(index=True)

    content: str = Field(sa_column=Column(Text))
    chunk_agent_metadata: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))

    start_position: int = Field(default=0)
    end_position: int = Field(default=0)
    page_number: Optional[int] = Field(default=None)
    section_title: Optional[str] = Field(default=None, max_length=255)

    embedding_model: str = Field(max_length=100)
    embedding_dimension: int = Field(default=1536)
    quality_score: float = Field(default=1.0)
    token_count: int = Field(default=0)

    created_at: datetime = Field(default_factory=datetime.utcnow)


__all__ = ["RAGDocumentModel", "RAGDocumentChunkModel"]
