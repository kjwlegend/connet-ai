"""
User Schemas

This module contains Pydantic schemas for user-related operations.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import EmailStr, Field, validator

from .base import BaseSchema, TimestampMixin, UUIDMixin


class UserBase(BaseSchema):
    """Base user schema."""
    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username")
    is_active: bool = Field(True, description="Whether user is active")


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(..., min_length=8, description="User password")
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserUpdate(BaseSchema):
    """Schema for updating a user."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    is_active: Optional[bool] = None


class UserResponse(UUIDMixin, UserBase, TimestampMixin):
    """Schema for user responses."""
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")
    permissions: Optional[List[str]] = Field(None, description="User permissions")
    roles: Optional[List[str]] = Field(None, description="User roles")
    
    @classmethod
    def from_user(cls, user: "User") -> "UserResponse":
        """Create response from user entity."""
        return cls(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            username=user.username,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=getattr(user, 'last_login_at', None),
            permissions=getattr(user, 'permissions', []),
            roles=getattr(user, 'roles', []),
        )


class UserUpdateRequest(BaseSchema):
    """Schema for user update requests."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=50)


# User entity (simplified for now)
class User(UUIDMixin, UserBase, TimestampMixin):
    """User entity."""
    password_hash: str = Field(..., description="Hashed password")
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")
    permissions: Optional[List[str]] = Field(None, description="User permissions")
    roles: Optional[List[str]] = Field(None, description="User roles")