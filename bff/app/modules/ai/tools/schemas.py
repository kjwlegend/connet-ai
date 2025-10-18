"""Schemas for AI tools and related webhooks."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ToolBase(BaseModel):
    """Shared tool attributes."""

    name: str = Field(..., max_length=255, description="Internal tool name")
    display_name: str = Field(..., max_length=255, description="Display name")
    description: str = Field(..., description="Tool description")


class ToolCreate(ToolBase):
    """Payload for creating a tool."""

    tool_type: str = Field(..., description="Tool type identifier")
    version: Optional[str] = Field(
        default="1.0.0", max_length=50, description="Tool version"
    )
    configuration: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Tool configuration metadata"
    )
    parameters_schema: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Parameters schema"
    )
    required_permissions: Optional[List[str]] = Field(
        default_factory=list, description="Required permissions"
    )
    timeout_seconds: Optional[int] = Field(
        default=30, description="Execution timeout in seconds"
    )
    rate_limit: Optional[Dict[str, int]] = Field(
        None, description="Rate limit configuration"
    )
    resource_limits: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Resource limits"
    )
    security_level: Optional[str] = Field(
        default="medium", description="Security level"
    )
    allowed_domains: Optional[List[str]] = Field(
        default_factory=list, description="Allowed domains"
    )
    blocked_patterns: Optional[List[str]] = Field(
        default_factory=list, description="Disallowed patterns"
    )
    status: Optional[str] = Field(default="active", description="Tool status")
    category: Optional[str] = Field(default="general", description="Tool category")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tool tags")


class ToolUpdate(BaseModel):
    """Payload for updating a tool."""

    name: Optional[str] = Field(None, max_length=255, description="Internal name")
    display_name: Optional[str] = Field(
        None, max_length=255, description="Display name"
    )
    description: Optional[str] = Field(None, description="Tool description")
    version: Optional[str] = Field(None, max_length=50, description="Tool version")
    configuration: Optional[Dict[str, Any]] = Field(
        None, description="Tool configuration metadata"
    )
    parameters_schema: Optional[Dict[str, Any]] = Field(
        None, description="Parameters schema"
    )
    required_permissions: Optional[List[str]] = Field(
        None, description="Required permissions"
    )
    timeout_seconds: Optional[int] = Field(
        None, description="Execution timeout in seconds"
    )
    rate_limit: Optional[Dict[str, int]] = Field(
        None, description="Rate limit configuration"
    )
    resource_limits: Optional[Dict[str, Any]] = Field(
        None, description="Resource limits"
    )
    security_level: Optional[str] = Field(None, description="Security level")
    allowed_domains: Optional[List[str]] = Field(
        None, description="Allowed domains"
    )
    blocked_patterns: Optional[List[str]] = Field(
        None, description="Disallowed patterns"
    )
    status: Optional[str] = Field(None, description="Tool status")
    category: Optional[str] = Field(None, description="Tool category")
    tags: Optional[List[str]] = Field(None, description="Tool tags")


class ToolResponse(ToolBase):
    """Response model for tools."""

    id: UUID
    tool_type: str
    version: str = "1.0.0"
    configuration: Dict[str, Any] = {}
    parameters_schema: Dict[str, Any] = {}
    required_permissions: List[str] = []
    timeout_seconds: int = 30
    rate_limit: Optional[Dict[str, int]] = None
    resource_limits: Dict[str, Any] = {}
    security_level: str = "medium"
    allowed_domains: List[str] = []
    blocked_patterns: List[str] = []
    status: str = "active"
    category: str = "general"
    tags: List[str] = []
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    usage_count: int = 0
    success_rate: float = 1.0
    avg_execution_time: float = 0.0

    class Config:
        from_attributes = True


class ToolExecutionRequest(BaseModel):
    """Execution request payload for a tool."""

    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Execution parameters"
    )
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Execution context"
    )


class ToolExecutionResponse(BaseModel):
    """Response payload for a tool execution."""

    tool_id: UUID
    execution_id: str
    user_id: UUID
    parameters: Dict[str, Any] = {}
    result: Optional[Dict[str, Any]] = None
    success: bool = False
    error_message: Optional[str] = None
    execution_time: float = 0.0
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WebhookBase(BaseModel):
    """Shared webhook attributes."""

    name: str = Field(..., max_length=255, description="Webhook name")
    url: str = Field(..., max_length=1000, description="Destination URL")


class WebhookCreate(WebhookBase):
    """Payload for creating a webhook."""

    method: Optional[str] = Field(
        default="POST", max_length=10, description="HTTP method"
    )
    headers: Optional[Dict[str, str]] = Field(
        default_factory=dict, description="HTTP headers"
    )
    secret: Optional[str] = Field(None, max_length=255, description="Webhook secret")
    timeout_seconds: Optional[int] = Field(
        default=30, description="Request timeout in seconds"
    )
    retry_enabled: Optional[bool] = Field(
        default=True, description="Enable automatic retries"
    )
    max_retries: Optional[int] = Field(
        default=3, description="Maximum retries before giving up"
    )
    retry_delay_seconds: Optional[int] = Field(
        default=60, description="Delay between retries"
    )
    event_types: Optional[List[str]] = Field(
        default_factory=list, description="Supported event types"
    )
    event_filters: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Filter settings"
    )
    transform_template: Optional[str] = Field(
        None, description="Optional templating for payload transformation"
    )
    status: Optional[str] = Field(default="active", description="Webhook status")


class WebhookUpdate(BaseModel):
    """Payload for updating a webhook."""

    name: Optional[str] = Field(None, max_length=255, description="Webhook name")
    url: Optional[str] = Field(None, max_length=1000, description="Destination URL")
    method: Optional[str] = Field(None, max_length=10, description="HTTP method")
    headers: Optional[Dict[str, str]] = Field(
        None, description="HTTP headers"
    )
    secret: Optional[str] = Field(None, max_length=255, description="Webhook secret")
    timeout_seconds: Optional[int] = Field(
        None, description="Request timeout in seconds"
    )
    retry_enabled: Optional[bool] = Field(
        None, description="Enable automatic retries"
    )
    max_retries: Optional[int] = Field(
        None, description="Maximum retries before giving up"
    )
    retry_delay_seconds: Optional[int] = Field(
        None, description="Delay between retries"
    )
    event_types: Optional[List[str]] = Field(
        None, description="Supported event types"
    )
    event_filters: Optional[Dict[str, Any]] = Field(
        None, description="Filter settings"
    )
    transform_template: Optional[str] = Field(
        None, description="Optional templating for payload transformation"
    )
    status: Optional[str] = Field(None, description="Webhook status")


class WebhookResponse(WebhookBase):
    """Response model for webhook configuration."""

    id: UUID
    method: str = "POST"
    headers: Dict[str, str] = {}
    secret: Optional[str] = None
    timeout_seconds: int = 30
    retry_enabled: bool = True
    max_retries: int = 3
    retry_delay_seconds: int = 60
    event_types: List[str] = []
    event_filters: Dict[str, Any] = {}
    transform_template: Optional[str] = None
    status: str = "active"
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    total_triggers: int = 0
    successful_triggers: int = 0
    failed_triggers: int = 0
    last_triggered_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WebhookTriggerResponse(BaseModel):
    """Response model for webhook trigger events."""

    id: UUID
    webhook_id: UUID
    trigger_id: str
    event_type: str
    event_data: Dict[str, Any] = {}
    payload: Dict[str, Any] = {}
    status: str = "pending"
    success: bool = False
    http_status_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime
    sent_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


__all__ = [
    "ToolCreate",
    "ToolUpdate",
    "ToolResponse",
    "ToolExecutionRequest",
    "ToolExecutionResponse",
    "WebhookCreate",
    "WebhookUpdate",
    "WebhookResponse",
    "WebhookTriggerResponse",
]
