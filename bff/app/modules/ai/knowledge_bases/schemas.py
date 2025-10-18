"""Schemas for the knowledge_bases module."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class KnowledgeBaseBase(BaseModel):
    """Shared knowledge base attributes."""

    name: str = Field(..., max_length=255, description="Knowledge base name")
    description: Optional[str] = Field(
        None, description="Knowledge base description"
    )
    knowledge_type: str = Field(
        ..., max_length=100, description="Type of knowledge stored"
    )


class KnowledgeBaseCreate(KnowledgeBaseBase):
    """Payload for creating a knowledge base."""

    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata"
    )
    rag_config: Optional[Dict[str, Any]] = Field(
        None, description="Retrieval-augmented generation configuration"
    )
    tags: Optional[List[str]] = Field(default_factory=list, description="Tag list")
    knowledge_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Knowledge-specific metadata"
    )


class KnowledgeBaseUpdate(BaseModel):
    """Payload for updating a knowledge base."""

    name: Optional[str] = Field(None, max_length=255, description="Knowledge base name")
    description: Optional[str] = Field(
        None, description="Knowledge base description"
    )
    knowledge_type: Optional[str] = Field(
        None, max_length=100, description="Type of knowledge stored"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata"
    )
    rag_config: Optional[Dict[str, Any]] = Field(
        None, description="Retrieval-augmented generation configuration"
    )
    tags: Optional[List[str]] = Field(None, description="Tag list")
    knowledge_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Knowledge-specific metadata"
    )


class KnowledgeBaseResponse(KnowledgeBaseBase):
    """Response model for knowledge bases."""

    id: UUID
    owner_id: UUID
    metadata: Optional[Dict[str, Any]] = None
    document_ids: Optional[List[str]] = None
    rag_config: Optional[Dict[str, Any]] = None
    is_active: bool = True
    tags: List[str] = []
    knowledge_metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None

    class Config:
        from_attributes = True


class KnowledgeDocumentBase(BaseModel):
    """Shared knowledge document attributes."""

    title: str = Field(..., description="Document title")
    content: Optional[str] = Field(None, description="Document content")


class KnowledgeDocumentCreate(KnowledgeDocumentBase):
    """Payload for creating a knowledge document."""

    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Document metadata"
    )


class KnowledgeDocumentResponse(KnowledgeDocumentBase):
    """Response model for knowledge documents."""

    id: UUID
    knowledge_base_id: UUID
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

    class Config:
        from_attributes = True


__all__ = [
    "KnowledgeBaseCreate",
    "KnowledgeBaseUpdate",
    "KnowledgeBaseResponse",
    "KnowledgeDocumentCreate",
    "KnowledgeDocumentResponse",
]
