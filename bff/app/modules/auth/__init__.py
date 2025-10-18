"""Auth module public interface."""

from app.modules.auth.router import router
from app.modules.auth.service import SupabaseAuthService
from app.modules.auth.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    OAuthCallbackRequest,
    OAuthLoginResponse,
    OAuthUrlRequest,
    OAuthUrlResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenVerifyRequest,
    TokenVerifyResponse,
)

__all__ = [
    "router",
    "ChangePasswordRequest",
    "LoginRequest",
    "LoginResponse",
    "OAuthCallbackRequest",
    "OAuthLoginResponse",
    "OAuthUrlRequest",
    "OAuthUrlResponse",
    "PasswordResetConfirm",
    "PasswordResetRequest",
    "RefreshTokenRequest",
    "RegisterRequest",
    "TokenVerifyRequest",
    "TokenVerifyResponse",
    "SupabaseAuthService",
]
