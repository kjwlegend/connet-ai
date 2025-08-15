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
    
    # Invitation system
    invited_by_code: Optional[str] = Field(None, max_length=20, description="Invitation code used for registration")
    
    # Registration tracking
    registration_source: Optional[str] = Field(None, max_length=50, description="Registration source: web, mobile, api")
    registration_channel: Optional[str] = Field(None, max_length=50, description="Registration channel: organic, invite, social, campaign")
    
    # UTM parameters for marketing tracking
    utm_source: Optional[str] = Field(None, max_length=100, description="UTM source parameter")
    utm_medium: Optional[str] = Field(None, max_length=100, description="UTM medium parameter")
    utm_campaign: Optional[str] = Field(None, max_length=100, description="UTM campaign parameter")


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


class OAuthCallbackRequest(BaseSchema):
    """OAuth callback request schema."""
    code: str = Field(..., description="OAuth authorization code")
    state: Optional[str] = Field(None, description="OAuth state parameter")
    provider: str = Field(..., description="OAuth provider (google, github)")
    redirect_uri: str = Field(..., description="Redirect URI used in OAuth flow")


class OAuthLoginResponse(BaseSchema):
    """OAuth login response schema."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse = Field(..., description="User information")
    is_new_user: bool = Field(..., description="Whether this is a newly created user")


class OAuthUrlRequest(BaseSchema):
    """OAuth URL generation request schema."""
    provider: str = Field(..., description="OAuth provider (google, github)")
    redirect_uri: str = Field(..., description="Redirect URI for OAuth callback")
    state: Optional[str] = Field(None, description="Optional state parameter")


class OAuthUrlResponse(BaseSchema):
    """OAuth URL response schema."""
    url: str = Field(..., description="OAuth authorization URL")
    state: str = Field(..., description="State parameter for security")