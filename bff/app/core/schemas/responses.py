"""Common response schemas shared across modules."""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import Field

from app.core.schemas.base import BaseSchema

T = TypeVar("T")


class HealthResponse(BaseSchema):
    """Health check response schema."""

    status: str = Field(..., description="Service status indicator")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    environment: str = Field(..., description="Deployment environment")
    timestamp: datetime = Field(..., description="Response timestamp")


class MessageResponse(BaseSchema):
    """Generic response containing a message and optional data."""

    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(
        None, description="Optional structured payload"
    )


class StatusResponse(BaseSchema):
    """Boolean status response with optional code."""

    success: bool = Field(..., description="Indicates whether the operation succeeded")
    message: str = Field(..., description="Human readable summary")
    code: Optional[str] = Field(None, description="Machine readable status code")


class ValidationErrorResponse(BaseSchema):
    """Standard validation error response schema."""

    error: str = Field("validation_error", description="Error type identifier")
    message: str = Field(..., description="Summary of the validation error")
    errors: List[Any] = Field(..., description="Detailed validation errors")


class NotFoundResponse(BaseSchema):
    """Response returned when a resource is not found."""

    error: str = Field("not_found", description="Error type identifier")
    message: str = Field(..., description="Human readable explanation")
    resource: str = Field(..., description="Resource that could not be located")


class UnauthorizedResponse(BaseSchema):
    """Response returned when authentication is required."""

    error: str = Field("unauthorized", description="Error type identifier")
    message: str = Field(
        "Authentication required", description="Human readable explanation"
    )


class ForbiddenResponse(BaseSchema):
    """Response returned when the user lacks permissions."""

    error: str = Field("forbidden", description="Error type identifier")
    message: str = Field(
        "Insufficient permissions", description="Human readable explanation"
    )


class RateLimitResponse(BaseSchema):
    """Response returned when the caller is being rate limited."""

    error: str = Field("rate_limit_exceeded", description="Error type identifier")
    message: str = Field(..., description="Human readable explanation")
    retry_after: int = Field(
        ..., description="Seconds callers should wait before retrying"
    )


class ErrorResponse(BaseSchema):
    """Standard error payload."""

    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Human readable error message")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional structured details"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Error timestamp"
    )


class SuccessResponse(BaseSchema):
    """Standard success payload."""

    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(
        None, description="Optional structured response payload"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp"
    )


class PaginatedResponse(BaseSchema, Generic[T]):
    """Generic response wrapper for paginated lists."""

    items: List[T] = Field(..., description="List of items on the page")
    total: int = Field(..., description="Total number of available items")
    page: int = Field(..., description="Current page number (1-based)")
    size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of available pages")

    @property
    def has_next(self) -> bool:
        """Return True when another page is available."""
        return self.page < self.pages

    @property
    def has_prev(self) -> bool:
        """Return True when a previous page is available."""
        return self.page > 1
