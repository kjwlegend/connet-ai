"""AI Agent models for the database layer."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Column, JSON, Text, null
from sqlalchemy import Column, JSON
from sqlalchemy.dialects.postgresql import JSONB


class AIAgentModel(SQLModel, table=True):
    """AI Agent model (统一后的主模型)"""

    __tablename__ = "agents"

    # 1) Identity & Lifecycle

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique Agent identifier",
    )
    name: str = Field(
        unique=True,
        index=True,
        max_length=500,
        description="Agent name for mentions (@code_assistant)",
    )
    display_name: str = Field(
        max_length=100, description="Display name (e.g., 'Code Assistant')"
    )
    description: str = Field(
        nullable=True, max_length=500, description="Agent description and capabilities"
    )
    introduction: str = Field(
        nullable=True, max_length=500, description="Agent introduction"
    )
    agent_type: str = Field(
        max_length=100, description="Agent type: system/custom/specialized"
    )
    version: str = Field(
        default="1.0.0", max_length=50, description="Semantic version of the agent"
    )
    status: str = Field(
        default="active",
        max_length=50,
        description="Lifecycle status: active/inactive/deprecated",
    )

    # 2) Visibility & Ownership
    is_public: bool = Field(
        default=True, description="Whether agent is publicly discoverable"
    )
    is_active: bool = Field(
        default=True, description="Whether agent is active (compat with legacy)"
    )

    # 3) UI & Presentation
    avatar_url: Optional[str] = Field(
        default=None, max_length=500, description="Agent avatar image URL"
    )
    avatar_style: Optional[str] = Field(
        default="default",
        max_length=20,
        description="Avatar style: default/anime/realistic/abstract",
    )
    conversation_style: str = Field(
        default="professional",
        max_length=100,
        description="Conversation style: professional/casual/humorous",
    )

    # 4) Core Configuration
    system_prompt: str = Field(
        sa_column=Column(Text),
        description="System prompt for the agent",
    )
    personality_config: Dict[str, Any] = Field(
        default={},
        sa_column=Column(JSONB),
        description="Structured personality profile",
    )
    model_preferences: Dict[str, Any] = Field(
        default={}, sa_column=Column(JSONB), description="Model selection & defaults"
    )

    # 6) Capabilities & Permissions
    capabilities: List[str] = Field(
        default=[], sa_column=Column(JSONB), description="High-level capabilities tags"
    )
    required_permissions: List[str] = Field(
        default=[],
        sa_column=Column(JSONB),
        description="Required permissions for sensitive ops",
    )
    # NOTE: Tools are now managed per-contact via ContactToolLink

    # 7) Categorization & Discovery
    tags: List[str] = Field(
        default=[], sa_column=Column(JSONB), description="Categorization tags"
    )
    category: Optional[str] = Field(
        default=None, index=True, max_length=50, description="Primary category"
    )

    # 8) Usage & Metrics
    usage_count: int = Field(default=0, description="Total usage count")
    follower_count: int = Field(default=0, description="Number of followers")

    # 9) Extensions & Embeddings
    agent_metadata: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSONB), description="Additional agent metadata"
    )
    description_embedding: Optional[List[float]] = Field(
        default=None, sa_column=Column(JSONB), description="Embedding of description"
    )
    capabilities_embedding: Optional[List[float]] = Field(
        default=None, sa_column=Column(JSONB), description="Embedding of capabilities"
    )

    # 10) LangGraph Integration Fields (New)
    node_type: Optional[str] = Field(
        default="standard",
        max_length=50, 
        description="LangGraph node type: standard, workflow, tool, memory, router"
    )
    execution_config: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB),
        description="Execution configuration for LangGraph nodes"
    )
    resource_limits: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB),
        description="Resource limits (memory, CPU, timeout, etc.)"
    )
    dependencies: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB),
        description="Agent dependencies and requirements"
    )

    # 11) Timestamps
    created_by: UUID = Field(foreign_key="users.id", description="Creator user ID")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )
    last_used_at: Optional[datetime] = Field(
        default=None, description="Last used timestamp"
    )

    # OpenAPI 文档示例
    model_config = {
        "protected_namespaces": (),
        "json_schema_extra": {
            "example": {
                "name": "code_assistant",
                "display_name": "Code Assistant",
                "description": "Expert AI assistant for code generation, debugging, and guidance",
                "agent_type": "custom",
                "version": "1.0.0",
                "status": "active",
                "is_public": True,
                "is_active": True,
                "avatar_url": "https://example.com/avatar.png",
                "avatar_style": "default",
                "color_theme": "#4F46E5",
                "conversation_style": "professional",
                "system_prompt": "You are a helpful coding assistant...",
                "personality_config": {
                    "role": "Developer Assistant",
                    "expertise": ["Python", "SQL", "System Design"],
                    "communication_style": "professional",
                },
                "model_preferences": {
                    "default_model": "gpt-4.1-mini",
                    "fallback_models": ["gpt-4o", "claude-3.5"],
                    "temperature": 0.7,
                    "max_tokens": 8000,
                    "top_p": 1.0,
                    "presence_penalty": 0.0,
                    "frequency_penalty": 0.0,
                },
                "capabilities": ["code_generation", "debugging", "code_review"],
                "required_permissions": [],
                "max_context_length": 4000,
                "tags": ["coding", "assistant", "technical"],
                "category": "development",
                "usage_count": 120,
                "follower_count": 36,
                "agent_metadata": {"lang": "en"},
                "description_embedding": None,
                "capabilities_embedding": None,
            }
        }
    }


class AIAgentVersionModel(SQLModel, table=True):
    """AI Agent version history model"""

    __tablename__ = "ai_agent_versions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    agent_id: UUID = Field(foreign_key="agents.id", index=True)
    version_number: str = Field(max_length=50)
    previous_version: Optional[str] = Field(default=None, max_length=50)

    # Version data
    agent_snapshot: Dict[str, Any] = Field(sa_column=Column(JSONB))
    changes: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    change_description: Optional[str] = Field(default=None, sa_column=Column(Text))

    # Metadata
    created_by: UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_current: bool = Field(default=True)

