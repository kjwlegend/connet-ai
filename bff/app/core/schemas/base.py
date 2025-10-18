"""Shared base schema utilities."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    """Base schema with common configuration defaults."""

    model_config = {
        "from_attributes": True,
        "validate_assignment": True,
        "use_enum_values": True,
        "json_encoders": {
            datetime: lambda value: value.isoformat(),
            UUID: lambda value: str(value),
        },
    }


class TimestampMixin(BaseModel):
    """Mixin for schemas that expose creation/update timestamps."""

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class UUIDMixin(BaseModel):
    """Mixin for schemas with a UUID primary identifier."""

    id: str = Field(..., description="Unique identifier")
