"""
User Schemas

This module contains Pydantic schemas for user-related operations.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import EmailStr, Field, field_validator

from .base import BaseSchema, TimestampMixin, UUIDMixin


class UserBase(BaseSchema):
    """Base user schema."""

    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name")
    username: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Username"
    )
    is_active: bool = Field(True, description="Whether user is active")


class UserCreate(UserBase):
    """Schema for creating a user."""

    id: Optional[UUID] = Field(
        None, description="User ID (for external auth providers)"
    )
    password: Optional[str] = Field(
        None, min_length=8, description="User password (optional for OAuth)"
    )
    password_hash: Optional[str] = Field(None, description="Pre-hashed password")
    auth_provider: str = Field("local", description="Authentication provider")
    external_id: Optional[str] = Field(None, description="External provider user ID")

    # Invitation system
    invitation_code: Optional[str] = Field(
        None, description="User's unique invitation code"
    )
    invited_by_code: Optional[str] = Field(
        None, description="Invitation code used during registration"
    )
    invited_by_user_id: Optional[UUID] = Field(
        None, description="ID of the user who invited this user"
    )

    # Registration tracking
    registration_source: Optional[str] = Field(
        None, description="Registration source: web, mobile, api, admin"
    )
    registration_channel: Optional[str] = Field(
        None, description="Registration channel: organic, invite, social, campaign"
    )
    utm_source: Optional[str] = Field(None, description="UTM source parameter")
    utm_medium: Optional[str] = Field(None, description="UTM medium parameter")
    utm_campaign: Optional[str] = Field(None, description="UTM campaign parameter")

    user_metadata: Optional[dict] = Field(None, description="Additional user metadata")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """Validate password strength."""
        if v and len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class UserUpdate(BaseSchema):
    """Schema for updating a user."""

    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    is_active: Optional[bool] = None


class UserResponse(UUIDMixin, UserBase, TimestampMixin):
    """Schema for user responses."""

    invitation_code: Optional[str] = Field(
        None, description="User's unique invitation code"
    )
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")
    permissions: Optional[List[str]] = Field(None, description="User permissions")
    roles: Optional[List[str]] = Field(None, description="User roles")
    is_verified: bool = Field(False, description="Whether user email is verified")

    model_config = {"from_attributes": True}

    @classmethod
    def from_user(cls, user: "User") -> "UserResponse":
        """Create response from user entity."""
        return cls(
            id=str(user.id),  # Convert UUID to string
            email=user.email,
            full_name=user.full_name,
            username=user.username,
            is_active=user.is_active,
            is_verified=getattr(user, "is_verified", False),
            invitation_code=getattr(user, "invitation_code", None),
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=getattr(user, "last_login_at", None),
            permissions=getattr(user, "permissions", []),
            roles=getattr(user, "roles", []),
        )


class UserUpdateRequest(BaseSchema):
    """Schema for user update requests."""

    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=50)


# User entity (simplified for now)
class User(UUIDMixin, UserBase, TimestampMixin):
    """User entity."""

    password_hash: Optional[str] = Field(
        None, description="Hashed password (optional for OAuth)"
    )
    auth_provider: str = Field("local", description="Authentication provider")
    external_id: Optional[str] = Field(None, description="External provider user ID")
    is_verified: bool = Field(False, description="Whether user email is verified")

    # Invitation system
    invitation_code: Optional[str] = Field(
        None, description="User's unique invitation code"
    )
    invited_by_code: Optional[str] = Field(
        None, description="Invitation code used during registration"
    )
    invited_by_user_id: Optional[UUID] = Field(
        None, description="ID of the user who invited this user"
    )

    # Registration tracking
    registration_source: Optional[str] = Field(None, description="Registration source")
    registration_channel: Optional[str] = Field(
        None, description="Registration channel"
    )
    utm_source: Optional[str] = Field(None, description="UTM source parameter")
    utm_medium: Optional[str] = Field(None, description="UTM medium parameter")
    utm_campaign: Optional[str] = Field(None, description="UTM campaign parameter")

    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")
    permissions: Optional[List[str]] = Field(None, description="User permissions")
    roles: Optional[List[str]] = Field(None, description="User roles")
    user_metadata: Optional[dict] = Field(None, description="Additional user metadata")
