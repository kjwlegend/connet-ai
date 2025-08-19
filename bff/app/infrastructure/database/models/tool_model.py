from sqlmodel import SQLModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum
from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import JSONB
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import Enum as SAEnum


class ToolType(str, Enum):
    function_call = "function_call"
    mcp = "mcp"
    agent = "agent"
    webhook = "webhook"
    api = "api"
    file = "file"
    database = "database"
    other = "other"


class ToolModel(SQLModel, table=True):
    """AI Tool model for external integrations"""

    __tablename__ = "tools"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255, index=True, unique=True)
    display_name: str = Field(max_length=255)
    description: str = Field(sa_column=Column(Text))
    tool_type: ToolType = Field(
        sa_column=Column(SAEnum(ToolType, name="tool_type", native_enum=False))
    )
    version: str = Field(default="1.0.0", max_length=50)

    # Tool configuration
    configuration: Dict[str, Any] = Field(sa_column=Column(JSONB))
    parameters_schema: Dict[str, Any] = Field(sa_column=Column(JSONB))
    required_permissions: List[str] = Field(default=[], sa_column=Column(JSONB))

    # Execution settings
    timeout_seconds: int = Field(default=30)
    rate_limit: Optional[Dict[str, int]] = Field(default=None, sa_column=Column(JSONB))
    resource_limits: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))

    # Security and access
    security_level: str = Field(default="medium", max_length=50)  # low, medium, high
    allowed_domains: List[str] = Field(default=[], sa_column=Column(JSONB))
    blocked_patterns: List[str] = Field(default=[], sa_column=Column(JSONB))

    # Status and metadata
    status: str = Field(default="active", max_length=50)  # active, inactive, deprecated
    category: str = Field(default="general", max_length=100)
    tags: List[str] = Field(default=[], sa_column=Column(JSONB))

    created_by: UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Usage statistics
    usage_count: int = Field(default=0)
    success_rate: float = Field(default=1.0)
    avg_execution_time: float = Field(default=0.0)


class WebhookModel(SQLModel, table=True):
    """AI Webhook model for external integrations"""

    __tablename__ = "webhooks_tool"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255)
    url: str = Field(max_length=1000)
    method: str = Field(default="POST", max_length=10)

    # Configuration
    headers: Dict[str, str] = Field(default={}, sa_column=Column(JSONB))
    secret: Optional[str] = Field(
        default=None, max_length=255
    )  # For signature verification
    timeout_seconds: int = Field(default=30)

    # Retry configuration
    retry_enabled: bool = Field(default=True)
    max_retries: int = Field(default=3)
    retry_delay_seconds: int = Field(default=60)

    # Event filters
    event_types: List[str] = Field(default=[], sa_column=Column(JSONB))
    event_filters: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    transform_template: Optional[str] = Field(default=None, sa_column=Column(Text))

    # Status and metadata
    status: str = Field(default="active", max_length=50)  # active, inactive, failed
    created_by: UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Statistics
    total_triggers: int = Field(default=0)
    successful_triggers: int = Field(default=0)
    failed_triggers: int = Field(default=0)
    last_triggered_at: Optional[datetime] = Field(default=None)


class WebhookTriggerModel(SQLModel, table=True):
    """Webhook trigger history model"""

    __tablename__ = "webhook_triggers"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    webhook_id: UUID = Field(foreign_key="webhooks_tool.id", index=True)
    trigger_id: str = Field(max_length=255, index=True)

    # Trigger details
    event_type: str = Field(max_length=100)
    event_data: Dict[str, Any] = Field(sa_column=Column(JSONB))
    payload: Dict[str, Any] = Field(sa_column=Column(JSONB))

    # Execution details
    status: str = Field(max_length=50)  # pending, sent, completed, failed, retry
    success: bool = Field(default=False)
    http_status_code: Optional[int] = Field(default=None)
    response_body: Optional[str] = Field(default=None, sa_column=Column(Text))
    response_headers: Dict[str, str] = Field(default={}, sa_column=Column(JSONB))

    # Error handling
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)
    next_retry_at: Optional[datetime] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
