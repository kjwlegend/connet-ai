"""
Knowledge Base API Schemas
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


# Base schemas
class KnowledgeBaseBase(BaseModel):
    name: str = Field(..., max_length=255, description="Knowledge base name")
    description: Optional[str] = Field(None, description="Knowledge base description")
    knowledge_type: str = Field(..., max_length=100, description="Type of knowledge")


# Request schemas
class KnowledgeBaseCreate(KnowledgeBaseBase):
    """Schema for creating a knowledge base."""
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    rag_config: Optional[Dict[str, Any]] = Field(None, description="RAG configuration")
    tags: Optional[List[str]] = Field([], description="Tags for categorization")
    knowledge_metadata: Optional[Dict[str, Any]] = Field({}, description="Knowledge-specific metadata")


class KnowledgeBaseUpdate(BaseModel):
    """Schema for updating a knowledge base."""
    name: Optional[str] = Field(None, max_length=255, description="Knowledge base name")
    description: Optional[str] = Field(None, description="Knowledge base description")
    knowledge_type: Optional[str] = Field(None, max_length=100, description="Type of knowledge")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    rag_config: Optional[Dict[str, Any]] = Field(None, description="RAG configuration")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")
    knowledge_metadata: Optional[Dict[str, Any]] = Field(None, description="Knowledge-specific metadata")


# Response schemas
class KnowledgeBaseResponse(KnowledgeBaseBase):
    """Schema for knowledge base response."""
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


# Knowledge Document schemas
class KnowledgeDocumentBase(BaseModel):
    title: str = Field(..., description="Document title")
    content: Optional[str] = Field(None, description="Document content")


class KnowledgeDocumentCreate(KnowledgeDocumentBase):
    """Schema for creating a knowledge document."""
    metadata: Optional[Dict[str, Any]] = Field(None, description="Document metadata")


class KnowledgeDocumentResponse(KnowledgeDocumentBase):
    """Schema for knowledge document response."""
    id: UUID
    knowledge_base_id: UUID
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

    class Config:
        from_attributes = True


# RAG Document schemas
class RAGDocumentBase(BaseModel):
    name: str = Field(..., max_length=255, description="Document name")
    content: str = Field(..., description="Document content")


class RAGDocumentCreate(RAGDocumentBase):
    """Schema for creating a RAG document."""
    file_path: Optional[str] = Field(None, max_length=1000, description="File path")
    file_type: str = Field(..., max_length=100, description="File type")
    file_size: int = Field(0, description="File size in bytes")
    visibility: Optional[str] = Field("private", description="Document visibility")
    shared_with: Optional[List[UUID]] = Field([], description="Users to share with")
    agent_metadata: Optional[Dict[str, Any]] = Field({}, description="Agent metadata")


class RAGDocumentResponse(RAGDocumentBase):
    """Schema for RAG document response."""
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