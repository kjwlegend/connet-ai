"""
Response Schemas

This module contains common response schemas used across the API.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Generic, TypeVar

from pydantic import Field

from .base import BaseSchema

T = TypeVar('T')


class HealthResponse(BaseSchema):
    """Health check response schema."""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    environment: str = Field(..., description="Environment name")
    timestamp: datetime = Field(..., description="Response timestamp")


class MessageResponse(BaseSchema):
    """Generic message response."""
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")


class StatusResponse(BaseSchema):
    """Status response schema."""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Status message")
    code: Optional[str] = Field(None, description="Status code")


class ValidationErrorResponse(BaseSchema):
    """Validation error response schema."""
    error: str = Field("validation_error", description="Error type")
    message: str = Field(..., description="Error message")
    errors: list = Field(..., description="List of validation errors")


class NotFoundResponse(BaseSchema):
    """Not found error response schema."""
    error: str = Field("not_found", description="Error type")
    message: str = Field(..., description="Error message")
    resource: str = Field(..., description="Resource that was not found")


class UnauthorizedResponse(BaseSchema):
    """Unauthorized error response schema."""
    error: str = Field("unauthorized", description="Error type")
    message: str = Field("Authentication required", description="Error message")


class ForbiddenResponse(BaseSchema):
    """Forbidden error response schema."""
    error: str = Field("forbidden", description="Error type")
    message: str = Field("Insufficient permissions", description="Error message")


class RateLimitResponse(BaseSchema):
    """Rate limit error response schema."""
    error: str = Field("rate_limit_exceeded", description="Error type")
    message: str = Field(..., description="Error message")
    retry_after: int = Field(..., description="Seconds to wait before retrying")


class PaginationMeta(BaseSchema):
    """Pagination metadata."""
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class PaginatedResponse(BaseSchema, Generic[T]):
    """Paginated response schema."""
    items: List[T] = Field(..., description="List of items")
    meta: PaginationMeta = Field(..., description="Pagination metadata")