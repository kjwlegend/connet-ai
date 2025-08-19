"""
Tools API Schemas
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


# Base schemas
class ToolBase(BaseModel):
    name: str = Field(..., max_length=255, description="Tool name")
    display_name: str = Field(..., max_length=255, description="Display name")
    description: str = Field(..., description="Tool description")


# Request schemas
class ToolCreate(ToolBase):
    """Schema for creating a tool."""
    tool_type: str = Field(..., description="Tool type")
    version: Optional[str] = Field("1.0.0", max_length=50, description="Tool version")
    configuration: Optional[Dict[str, Any]] = Field({}, description="Tool configuration")
    parameters_schema: Optional[Dict[str, Any]] = Field({}, description="Parameters schema")
    required_permissions: Optional[List[str]] = Field([], description="Required permissions")
    timeout_seconds: Optional[int] = Field(30, description="Timeout in seconds")
    rate_limit: Optional[Dict[str, int]] = Field(None, description="Rate limit configuration")
    resource_limits: Optional[Dict[str, Any]] = Field({}, description="Resource limits")
    security_level: Optional[str] = Field("medium", description="Security level")
    allowed_domains: Optional[List[str]] = Field([], description="Allowed domains")
    blocked_patterns: Optional[List[str]] = Field([], description="Blocked patterns")
    status: Optional[str] = Field("active", description="Tool status")
    category: Optional[str] = Field("general", description="Tool category")
    tags: Optional[List[str]] = Field([], description="Tool tags")


class ToolUpdate(BaseModel):
    """Schema for updating a tool."""
    name: Optional[str] = Field(None, max_length=255, description="Tool name")
    display_name: Optional[str] = Field(None, max_length=255, description="Display name")
    description: Optional[str] = Field(None, description="Tool description")
    version: Optional[str] = Field(None, max_length=50, description="Tool version")
    configuration: Optional[Dict[str, Any]] = Field(None, description="Tool configuration")
    parameters_schema: Optional[Dict[str, Any]] = Field(None, description="Parameters schema")
    required_permissions: Optional[List[str]] = Field(None, description="Required permissions")
    timeout_seconds: Optional[int] = Field(None, description="Timeout in seconds")
    rate_limit: Optional[Dict[str, int]] = Field(None, description="Rate limit configuration")
    resource_limits: Optional[Dict[str, Any]] = Field(None, description="Resource limits")
    security_level: Optional[str] = Field(None, description="Security level")
    allowed_domains: Optional[List[str]] = Field(None, description="Allowed domains")
    blocked_patterns: Optional[List[str]] = Field(None, description="Blocked patterns")
    status: Optional[str] = Field(None, description="Tool status")
    category: Optional[str] = Field(None, description="Tool category")
    tags: Optional[List[str]] = Field(None, description="Tool tags")


# Response schemas
class ToolResponse(ToolBase):
    """Schema for tool response."""
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


# Tool Execution schemas
class ToolExecutionRequest(BaseModel):
    """Schema for tool execution request."""
    parameters: Dict[str, Any] = Field({}, description="Execution parameters")
    context: Optional[Dict[str, Any]] = Field({}, description="Execution context")


class ToolExecutionResponse(BaseModel):
    """Schema for tool execution response."""
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


# Webhook schemas
class WebhookBase(BaseModel):
    name: str = Field(..., max_length=255, description="Webhook name")
    url: str = Field(..., max_length=1000, description="Webhook URL")


class WebhookCreate(WebhookBase):
    """Schema for creating a webhook."""
    method: Optional[str] = Field("POST", max_length=10, description="HTTP method")
    headers: Optional[Dict[str, str]] = Field({}, description="HTTP headers")
    secret: Optional[str] = Field(None, max_length=255, description="Webhook secret")
    timeout_seconds: Optional[int] = Field(30, description="Timeout in seconds")
    retry_enabled: Optional[bool] = Field(True, description="Enable retries")
    max_retries: Optional[int] = Field(3, description="Maximum retries")
    retry_delay_seconds: Optional[int] = Field(60, description="Retry delay in seconds")
    event_types: Optional[List[str]] = Field([], description="Event types to handle")
    event_filters: Optional[Dict[str, Any]] = Field({}, description="Event filters")
    transform_template: Optional[str] = Field(None, description="Transform template")
    status: Optional[str] = Field("active", description="Webhook status")


class WebhookUpdate(BaseModel):
    """Schema for updating a webhook."""
    name: Optional[str] = Field(None, max_length=255, description="Webhook name")
    url: Optional[str] = Field(None, max_length=1000, description="Webhook URL")
    method: Optional[str] = Field(None, max_length=10, description="HTTP method")
    headers: Optional[Dict[str, str]] = Field(None, description="HTTP headers")
    secret: Optional[str] = Field(None, max_length=255, description="Webhook secret")
    timeout_seconds: Optional[int] = Field(None, description="Timeout in seconds")
    retry_enabled: Optional[bool] = Field(None, description="Enable retries")
    max_retries: Optional[int] = Field(None, description="Maximum retries")
    retry_delay_seconds: Optional[int] = Field(None, description="Retry delay in seconds")
    event_types: Optional[List[str]] = Field(None, description="Event types to handle")
    event_filters: Optional[Dict[str, Any]] = Field(None, description="Event filters")
    transform_template: Optional[str] = Field(None, description="Transform template")
    status: Optional[str] = Field(None, description="Webhook status")


class WebhookResponse(WebhookBase):
    """Schema for webhook response."""
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


# Webhook Trigger schemas
class WebhookTriggerResponse(BaseModel):
    """Schema for webhook trigger response."""
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