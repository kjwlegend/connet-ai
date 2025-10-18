"""Schemas for the AI RAG module."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RAGDocumentBase(BaseModel):
    """Shared attributes for RAG documents."""

    name: str = Field(..., max_length=255, description="Document name")
    content: str = Field(..., description="Document content")


class RAGDocumentCreate(RAGDocumentBase):
    """Payload for creating a RAG document."""

    file_path: Optional[str] = Field(
        None, max_length=1000, description="Path to the source file"
    )
    file_type: str = Field(..., max_length=100, description="File type")
    file_size: int = Field(0, description="File size in bytes")
    visibility: Optional[str] = Field(
        "private", description="Document visibility (private/shared/public)"
    )
    shared_with: Optional[List[UUID]] = Field(
        default_factory=list, description="Users the document is shared with"
    )
    agent_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Agent-specific metadata"
    )


class RAGDocumentResponse(RAGDocumentBase):
    """Response model for RAG documents."""

    id: UUID
    file_path: Optional[str] = None
    file_type: str
    file_size: int = 0
    agent_metadata: Dict[str, Any] = {}
    processing_status: str = "pending"
    chunk_count: int = 0
    quality_score: float = 1.0
    owner_id: UUID
    visibility: str = "private"
    shared_with: List[UUID] = []
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


__all__ = ["RAGDocumentCreate", "RAGDocumentResponse"]
