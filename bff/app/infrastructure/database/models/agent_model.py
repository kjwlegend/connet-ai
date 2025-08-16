"""
Agent Database Model

This module defines the SQLModel for AI agents in the database.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON


class AgentModel(SQLModel, table=True):
    """AI agent database model."""

    __tablename__ = "agents"

    # Primary key and basic information
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique agent identifier",
    )
    name: str = Field(
        unique=True,
        index=True,
        max_length=50,
        description="Agent name for mentions (@code_assistant)",
    )
    display_name: str = Field(
        max_length=100, description="Display name (e.g., 'Code Assistant')"
    )
    description: str = Field(
        max_length=500, description="Agent description and capabilities"
    )

    # Visual representation
    avatar_url: Optional[str] = Field(
        default=None, max_length=500, description="Agent avatar image URL"
    )
    avatar_style: Optional[str] = Field(
        default="default",
        max_length=20,
        description="Avatar style: default, anime, realistic, abstract",
    )
    color_theme: Optional[str] = Field(
        default=None,
        max_length=7,
        description="Agent theme color (hex format: #FF6B6B)",
    )

    # Agent configuration
    ai_model_config: dict = Field(
        sa_column=Column(JSON),
        description="AI model configuration {model, temperature, max_tokens}",
    )
    system_prompt: str = Field(
        max_length=2000, description="System prompt for the agent"
    )

    # Status and permissions
    is_active: bool = Field(default=True, description="Whether agent is active")
    is_public: bool = Field(
        default=True, description="Whether agent is publicly available"
    )
    created_by: UUID = Field(
        foreign_key="users.id", index=True, description="Creator user ID"
    )

    # Capabilities configuration (removed agent_type, using tags)
    capabilities: List[str] = Field(
        default=[], sa_column=Column(JSON), description="Agent capabilities list"
    )
    tools: List[str] = Field(
        default=[], sa_column=Column(JSON), description="Available tools list"
    )
    max_tokens: int = Field(default=2048, description="Maximum tokens per response")

    # Knowledge base association (summary info)
    knowledge_base_count: int = Field(
        default=0, description="Number of associated knowledge bases"
    )

    # Usage statistics
    usage_count: int = Field(default=0, description="Total usage count")
    success_rate: float = Field(default=0.0, description="Success rate (0.0 to 1.0)")
    avg_response_time: float = Field(
        default=0.0, description="Average response time in seconds"
    )
    follower_count: int = Field(default=0, description="Number of followers")

    # Social attributes (AI agents as community members)
    personality_traits: List[str] = Field(
        default=[], sa_column=Column(JSON), description="Personality traits list"
    )
    communication_style: Optional[str] = Field(
        default="professional",
        max_length=20,
        description="Communication style: casual, professional, humorous",
    )
    active_hours: Optional[dict] = Field(
        default=None, sa_column=Column(JSON), description="Active hours configuration"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Agent creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )
    last_active_at: Optional[datetime] = Field(
        default=None, description="Last active timestamp"
    )

    # Classification and discovery
    tags: List[str] = Field(
        default=[], sa_column=Column(JSON), description="Tags for categorization"
    )
    category: Optional[str] = Field(
        default=None, index=True, max_length=50, description="Primary category"
    )

    # Metadata
    agent_metadata: Optional[dict] = Field(
        default=None, sa_column=Column(JSON), description="Additional agent metadata"
    )

    # Vector embeddings (for semantic search)
    description_embedding: Optional[List[float]] = Field(
        default=None, sa_column=Column(JSON), description="Description vector embedding"
    )
    capabilities_embedding: Optional[List[float]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Capabilities vector embedding",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "code_assistant",
                "display_name": "Code Assistant",
                "description": "Expert AI assistant for code generation, debugging, and technical guidance",
                "avatar_style": "default",
                "color_theme": "#4F46E5",
                "ai_model_config": {
                    "model": "gpt-4",
                    "temperature": 0.7,
                    "max_tokens": 2048,
                },
                "system_prompt": "You are a helpful coding assistant...",
                "capabilities": ["code_generation", "debugging", "code_review"],
                "tools": ["python_executor", "file_reader", "web_search"],
                "personality_traits": ["helpful", "analytical", "precise"],
                "communication_style": "professional",
                "tags": ["coding", "assistant", "technical"],
                "category": "development",
                "is_public": True,
            }
        }
    }
