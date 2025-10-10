"""Models for AI tool and webhook management."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, SQLModel


class ToolType(str, Enum):
    """Enumeration of supported AI tool categories."""

    FUNCTION_CALL = "function_call"
    MCP = "mcp"
    AGENT = "agent"
    WEBHOOK = "webhook"
    API = "api"
    FILE = "file"
    DATABASE = "database"
    OTHER = "other"


class ToolModel(SQLModel, table=True):
    """AI tool definition for external integrations."""

    __tablename__ = "tools"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255, index=True, unique=True)
    display_name: str = Field(max_length=255)
    description: str = Field(sa_column=Column(Text))
    tool_type: ToolType = Field(
        sa_column=Column(SAEnum(ToolType, name="tool_type", native_enum=False))
    )
    version: str = Field(default="1.0.0", max_length=50)

    configuration: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    parameters_schema: Dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSONB)
    )
    required_permissions: List[str] = Field(
        default_factory=list, sa_column=Column(JSONB)
    )

    timeout_seconds: int = Field(default=30)
    rate_limit: Optional[Dict[str, int]] = Field(
        default=None, sa_column=Column(JSONB)
    )
    resource_limits: Dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSONB)
    )

    security_level: str = Field(default="medium", max_length=50)
    allowed_domains: List[str] = Field(default_factory=list, sa_column=Column(JSONB))
    blocked_patterns: List[str] = Field(default_factory=list, sa_column=Column(JSONB))

    status: str = Field(default="active", max_length=50)
    category: str = Field(default="general", max_length=100)
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSONB))

    created_by: UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    usage_count: int = Field(default=0)
    success_rate: float = Field(default=1.0)
    avg_execution_time: float = Field(default=0.0)


class WebhookModel(SQLModel, table=True):
    """Webhook configuration associated with AI tools."""

    __tablename__ = "webhooks_tool"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255)
    url: str = Field(max_length=1000)
    method: str = Field(default="POST", max_length=10)

    headers: Dict[str, str] = Field(default_factory=dict, sa_column=Column(JSONB))
    secret: Optional[str] = Field(default=None, max_length=255)
    timeout_seconds: int = Field(default=30)

    retry_enabled: bool = Field(default=True)
    max_retries: int = Field(default=3)
    retry_delay_seconds: int = Field(default=60)

    event_types: List[str] = Field(default_factory=list, sa_column=Column(JSONB))
    event_filters: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    transform_template: Optional[str] = Field(default=None, sa_column=Column(Text))

    status: str = Field(default="active", max_length=50)
    created_by: UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    total_triggers: int = Field(default=0)
    successful_triggers: int = Field(default=0)
    failed_triggers: int = Field(default=0)
    last_triggered_at: Optional[datetime] = Field(default=None)


class WebhookTriggerModel(SQLModel, table=True):
    """Execution history for tool webhooks."""

    __tablename__ = "webhook_triggers"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    webhook_id: UUID = Field(foreign_key="webhooks_tool.id", index=True)
    trigger_id: str = Field(max_length=255, index=True)

    event_type: str = Field(max_length=100)
    event_data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    payload: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))

    status: str = Field(max_length=50)
    success: bool = Field(default=False)
    http_status_code: Optional[int] = Field(default=None)
    response_body: Optional[str] = Field(default=None, sa_column=Column(Text))
    response_headers: Dict[str, str] = Field(
        default_factory=dict, sa_column=Column(JSONB)
    )

    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)
    next_retry_at: Optional[datetime] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)


__all__ = [
    "ToolType",
    "ToolModel",
    "WebhookModel",
    "WebhookTriggerModel",
]
