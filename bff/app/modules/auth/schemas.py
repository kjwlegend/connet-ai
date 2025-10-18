"""Authentication schemas scoped to the auth module."""

from typing import Optional

from pydantic import EmailStr, Field

from app.core.schemas import BaseSchema
from app.modules.users.schemas import UserResponse


class LoginRequest(BaseSchema):
    """Login request payload."""

    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")


class LoginResponse(BaseSchema):
    """Login response payload."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse = Field(..., description="Authenticated user information")


class RefreshTokenRequest(BaseSchema):
    """Refresh token request payload."""

    refresh_token: Optional[str] = Field(
        None, description="JWT refresh token (optional when using cookies)"
    )


class RegisterRequest(BaseSchema):
    """User registration request payload."""

    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="User password")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name")
    username: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Username"
    )
    invited_by_code: Optional[str] = Field(
        None, max_length=20, description="Invitation code provided during registration"
    )
    registration_source: Optional[str] = Field(
        None,
        max_length=50,
        description="Registration source (web, mobile, api, admin, etc.)",
    )
    registration_channel: Optional[str] = Field(
        None,
        max_length=50,
        description="Registration channel (organic, invite, social, campaign, etc.)",
    )
    utm_source: Optional[str] = Field(
        None, max_length=100, description="UTM source parameter"
    )
    utm_medium: Optional[str] = Field(
        None, max_length=100, description="UTM medium parameter"
    )
    utm_campaign: Optional[str] = Field(
        None, max_length=100, description="UTM campaign parameter"
    )


class TokenVerifyRequest(BaseSchema):
    """Token verification request payload."""

    token: str = Field(..., description="JWT token to verify")


class TokenVerifyResponse(BaseSchema):
    """Token verification response payload."""

    valid: bool = Field(..., description="Whether the token is valid")
    payload: Optional[dict] = Field(None, description="Token payload if valid")
    error: Optional[str] = Field(None, description="Error message if invalid")


class PasswordResetRequest(BaseSchema):
    """Password reset request payload."""

    email: EmailStr = Field(..., description="User email")


class PasswordResetConfirm(BaseSchema):
    """Password reset confirmation payload."""

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")


class ChangePasswordRequest(BaseSchema):
    """Change password request payload."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")


class OAuthCallbackRequest(BaseSchema):
    """OAuth callback request payload."""

    code: str = Field(..., description="OAuth authorization code")
    state: Optional[str] = Field(None, description="OAuth state parameter")
    provider: str = Field(..., description="OAuth provider identifier")
    redirect_uri: str = Field(..., description="Redirect URI used in the OAuth flow")


class OAuthLoginResponse(BaseSchema):
    """OAuth login response payload."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse = Field(..., description="Authenticated user information")
    is_new_user: bool = Field(..., description="Whether this is a newly created user")


class OAuthUrlRequest(BaseSchema):
    """OAuth URL generation request payload."""

    provider: str = Field(..., description="OAuth provider identifier")
    redirect_uri: str = Field(..., description="Redirect URI for the OAuth callback")
    state: Optional[str] = Field(None, description="Optional state parameter")


class OAuthUrlResponse(BaseSchema):
    """OAuth authorization URL response payload."""

    url: str = Field(..., description="OAuth authorization URL")
    state: str = Field(..., description="State parameter for CSRF protection")


__all__ = [
    "LoginRequest",
    "LoginResponse",
    "RefreshTokenRequest",
    "RegisterRequest",
    "TokenVerifyRequest",
    "TokenVerifyResponse",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "ChangePasswordRequest",
    "OAuthCallbackRequest",
    "OAuthLoginResponse",
    "OAuthUrlRequest",
    "OAuthUrlResponse",
]
