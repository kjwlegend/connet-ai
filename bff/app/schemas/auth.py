"""
Authentication Schemas

This module contains Pydantic schemas for authentication operations.
"""

from typing import List, Optional

from pydantic import EmailStr, Field

from .base import BaseSchema
from .user import UserResponse


class LoginRequest(BaseSchema):
    """Login request schema."""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")


class LoginResponse(BaseSchema):
    """Login response schema."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse = Field(..., description="User information")


class RefreshTokenRequest(BaseSchema):
    """Refresh token request schema."""
    refresh_token: str = Field(..., description="JWT refresh token")


class RegisterRequest(BaseSchema):
    """User registration request schema."""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="User password")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username")


class TokenVerifyRequest(BaseSchema):
    """Token verification request schema."""
    token: str = Field(..., description="JWT token to verify")


class TokenVerifyResponse(BaseSchema):
    """Token verification response schema."""
    valid: bool = Field(..., description="Whether token is valid")
    payload: Optional[dict] = Field(None, description="Token payload if valid")
    error: Optional[str] = Field(None, description="Error message if invalid")


class PasswordResetRequest(BaseSchema):
    """Password reset request schema."""
    email: EmailStr = Field(..., description="User email")


class PasswordResetConfirm(BaseSchema):
    """Password reset confirmation schema."""
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, description="New password")


class ChangePasswordRequest(BaseSchema):
    """Change password request schema."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")