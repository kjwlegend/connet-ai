"""
Knowledge base Data base model

This module defines RAG knowledge and relationship between knowledge/user/contacts

"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from sqlmodel import Column, Field, SQLModel, Text
from sqlalchemy import Column, JSON
from sqlalchemy import Enum
from sqlalchemy.dialects.postgresql import JSONB


class KnowledgeBaseModel(SQLModel, table=True):
    """
    KnowledgeBase
    """

    __tablename__ = "knowledge_database"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(sa_column=Column("name", Text, nullable=False, unique=True))
    description: Optional[str] = Field(
        default=None, sa_column=Column("description", Text, nullable=True)
    )
    knowledge_type: str = Field(
        max_length=100
    )  # documents, conversations, facts, procedures
    owner_id: Optional[UUID] = Field(default=None, foreign_key="users.id")

    # Example: list of document ids or embeddings references
    document_ids: Optional[List[str]] = Field(
        default=None, sa_column=Column(JSON, nullable=True)
    )
    # RAG-specific: store retriever config, embedding model, etc.
    rag_config: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON, nullable=True)
    )
    is_active: bool = Field(default=True, nullable=False)

    tags: List[str] = Field(default=[], sa_column=Column(JSON))
    knowledge_metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))

    created_at: datetime = Field(default_factory=datetime.now(), nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now(), nullable=False)
    created_by: Optional[UUID] = Field(default=None, foreign_key="users.id")


class KnowledgeDocumentModel(SQLModel, table=True):
    """
    Knowledge Document
    """

    __tablename__ = "knowledge_document"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    knowledge_base_id: UUID = Field(foreign_key="knowledge_database.id", nullable=False)
    title: str = Field(sa_column=Column("title", Text, nullable=False))
    content: Optional[str] = Field(
        default=None, sa_column=Column("content", Text, nullable=True)
    )
    knowledge_document_metadata: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON, nullable=True)
    )
    created_at: datetime = Field(default_factory=datetime.now(), nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now(), nullable=False)
    is_active: bool = Field(default=True, nullable=False)

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
    }


class RAGDocumentModel(SQLModel, table=True):
    """RAG document model for knowledge base"""

    __tablename__ = "rag_documents"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255)
    file_path: Optional[str] = Field(default=None, max_length=1000)
    file_type: str = Field(max_length=100)  # pdf, docx, txt, md, html, etc.
    file_size: int = Field(default=0)

    # Document content
    content: str = Field(sa_column=Column(Text))
    agent_metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))

    # Processing information
    processing_status: str = Field(
        default="pending", max_length=50
    )  # pending, processing, completed, fled
    chunk_count: int = Field(default=0)
    quality_score: float = Field(default=1.0)

    # Access control
    owner_id: UUID = Field(foreign_key="users.id")
    visibility: str = Field(default="private", max_length=50)  # private, shared, public
    shared_with: List[UUID] = Field(default=[], sa_column=Column(JSONB))

    created_at: datetime = Field(default_factory=datetime.now())
    updated_at: datetime = Field(default_factory=datetime.now())
    processed_at: Optional[datetime] = Field(default=None)


class RAGDocumentChunkModel(SQLModel, table=True):
    """RAG document chunk model for semantic search"""

    __tablename__ = "rag_document_chunks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    document_id: UUID = Field(foreign_key="rag_documents.id", index=True)
    chunk_index: int = Field(index=True)

    # Chunk content
    content: str = Field(sa_column=Column(Text))
    chunk_agent_metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))

    # Position information
    start_position: int = Field(default=0)
    end_position: int = Field(default=0)
    page_number: Optional[int] = Field(default=None)
    section_title: Optional[str] = Field(default=None, max_length=255)

    # Embedding information
    embedding_model: str = Field(max_length=100)
    embedding_dimension: int = Field(default=1536)
    # Note: actual embedding vectors stored in vector database

    # Quality and relevance
    quality_score: float = Field(default=1.0)
    token_count: int = Field(default=0)

    created_at: datetime = Field(default_factory=datetime.now())
