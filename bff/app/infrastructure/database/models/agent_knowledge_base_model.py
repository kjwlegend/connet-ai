"""
Agent Knowledge Base Association Database Model

This module defines the SQLModel for agent-knowledge base relationships in the database.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Field, SQLModel


class AgentKnowledgeBaseModel(SQLModel, table=True):
    """Agent knowledge base association database model."""
    
    __tablename__ = "agent_knowledge_bases"
    
    # Composite primary key
    agent_id: UUID = Field(
        foreign_key="agents.id",
        primary_key=True,
        description="Agent ID"
    )
    knowledge_base_id: str = Field(
        primary_key=True,
        max_length=100,
        description="Knowledge base system ID"
    )
    
    # Association configuration
    access_level: str = Field(
        default="read",
        max_length=20,
        description="Access level: read, write, admin"
    )
    priority: int = Field(
        default=1,
        description="Priority level, higher number = higher priority"
    )
    is_active: bool = Field(
        default=True,
        description="Whether this association is active"
    )
    
    # Usage configuration
    max_context_tokens: Optional[int] = Field(
        default=None,
        description="Maximum tokens to retrieve from this knowledge base"
    )
    retrieval_config: Optional[dict] = Field(
        default=None,
        description="Retrieval configuration parameters"
    )
    
    # Knowledge base information (redundant storage for fast queries)
    knowledge_base_name: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Knowledge base name"
    )
    knowledge_base_type: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Knowledge base type: documents, qa, code, custom"
    )
    
    # Statistics
    usage_count: int = Field(
        default=0,
        description="Number of times this knowledge base was used"
    )
    last_used_at: Optional[datetime] = Field(
        default=None,
        description="Last usage timestamp"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Association creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    # Metadata
    metadata: Optional[dict] = Field(
        default=None,
        description="Additional association metadata"
    )
    
    class Config:
        """SQLModel configuration."""
        schema_extra = {
            "example": {
                "agent_id": "12345678-1234-5678-9012-123456789012",
                "knowledge_base_id": "kb_python_docs_v3",
                "access_level": "read",
                "priority": 5,
                "max_context_tokens": 4000,
                "retrieval_config": {
                    "similarity_threshold": 0.8,
                    "max_results": 10,
                    "include_metadata": True
                },
                "knowledge_base_name": "Python Documentation v3.11",
                "knowledge_base_type": "documents",
                "usage_count": 142,
                "is_active": True
            }
        }