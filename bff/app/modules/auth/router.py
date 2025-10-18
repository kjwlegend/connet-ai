"""Authentication endpoints routed through the auth module."""

from typing import Optional

from fastapi import APIRouter, Body, Cookie, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials

from app.api.deps import (
    get_current_user,
    get_supabase_auth_service,
    get_user_service,
    security,
)
from app.config.settings import get_settings
from app.infrastructure.security.auth import JWTManager, get_jwt_manager
from app.modules.auth.schemas import (
    LoginRequest,
    LoginResponse,
    OAuthCallbackRequest,
    OAuthLoginResponse,
    OAuthUrlRequest,
    OAuthUrlResponse,
    PasswordResetRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenVerifyRequest,
)
from app.modules.users.schemas import UserResponse
from app.modules.users.service import UserService
from app.modules.auth.service import SupabaseAuthService
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse)
async def register(
    request: RegisterRequest,
    supabase_auth_service: SupabaseAuthService = Depends(get_supabase_auth_service),
) -> UserResponse:
    """Register a new user using Supabase Auth."""
    try:
        user, _ = await supabase_auth_service.register_user(
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            username=request.username,
            invited_by_code=request.invited_by_code,
            registration_source=request.registration_source,
            registration_channel=request.registration_channel,
            utm_source=request.utm_source,
            utm_medium=request.utm_medium,
            utm_campaign=request.utm_campaign,
        )

        logger.info("User registered successfully: %s", user.email)
        return UserResponse.from_user(user)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("Registration failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        ) from exc


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    response: Response,
    supabase_auth_service: SupabaseAuthService = Depends(get_supabase_auth_service),
    jwt_manager: JWTManager = Depends(get_jwt_manager),
) -> LoginResponse:
    """Authenticate user using Supabase Auth and return JWT tokens."""
    try:
        user, _ = await supabase_auth_service.login_user(
            email=request.email, password=request.password
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        access_token = jwt_manager.create_access_token(
            subject=str(user.id),
            scopes=user.permissions or [],
        )
        refresh_token = jwt_manager.create_refresh_token(subject=str(user.id))

        logger.info("User logged in successfully: %s", user.email)

        _set_refresh_cookie(response, refresh_token, jwt_manager)

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=jwt_manager.access_token_expire_minutes * 60,
            user=UserResponse.from_user(user),
        )

    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("Login failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed"
        ) from exc


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
    response: Response,
    request: Optional[RefreshTokenRequest] = Body(default=None),
    refresh_cookie: Optional[str] = Cookie(default=None, alias="refresh_token"),
    jwt_manager: JWTManager = Depends(get_jwt_manager),
    user_service: UserService = Depends(get_user_service),
) -> LoginResponse:
    """Refresh access token using refresh token."""
    try:
        token_value = (request.refresh_token if request else None) or refresh_cookie
        if not token_value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token missing",
            )

        payload = jwt_manager.verify_token(token_value)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        user = await user_service.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

        access_token = jwt_manager.create_access_token(
            subject=str(user.id),
            scopes=user.permissions or [],
        )
        new_refresh_token = jwt_manager.create_refresh_token(subject=str(user.id))

        logger.info("Token refreshed for user: %s", user.email)

        _set_refresh_cookie(response, new_refresh_token, jwt_manager)

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=jwt_manager.access_token_expire_minutes * 60,
            user=UserResponse.from_user(user),
        )
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover
        logger.error("Token refresh failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        ) from exc


@router.post("/verify")
async def verify_token(
    request: TokenVerifyRequest,
    jwt_manager: JWTManager = Depends(get_jwt_manager),
) -> dict:
    """Verify if a token is valid."""
    try:
        payload = jwt_manager.verify_token(request.token)
        return {
            "valid": True,
            "payload": {
                "sub": payload.get("sub"),
                "exp": payload.get("exp"),
                "iat": payload.get("iat"),
                "type": payload.get("type"),
                "scopes": payload.get("scopes", []),
            },
        }
    except Exception as exc:  # pragma: no cover
        return {"valid": False, "error": str(exc)}


@router.post("/logout")
async def logout(
    response: Response,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    jwt_manager: JWTManager = Depends(get_jwt_manager),
) -> dict:
    """Logout user by validating the token (placeholder for revocation)."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    jwt_manager.verify_token(credentials.credentials)
    _clear_refresh_cookie(response)
    logger.info("User logged out successfully")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user=Depends(get_current_user)) -> UserResponse:
    """Return the authenticated user's profile."""
    return UserResponse.from_user(current_user)


@router.post("/password-reset")
async def request_password_reset(
    request: PasswordResetRequest,
    supabase_auth_service: SupabaseAuthService = Depends(get_supabase_auth_service),
) -> dict:
    """Request password reset email via Supabase."""

    success = await supabase_auth_service.reset_password(
        email=request.email,
        redirect_to="http://localhost:3000/auth/reset-password",
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to send password reset email",
        )

    return {"message": "Password reset email sent successfully"}


@router.post("/verify-email")
async def verify_email(
    token: str,
    email: str,
    supabase_auth_service: SupabaseAuthService = Depends(get_supabase_auth_service),
) -> dict:
    """Verify a user's email address."""

    success = await supabase_auth_service.verify_email(token, email)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email verification failed",
        )

    return {"message": "Email verified successfully"}


@router.post("/oauth/url", response_model=OAuthUrlResponse)
async def get_oauth_url(
    request: OAuthUrlRequest,
    supabase_auth_service: SupabaseAuthService = Depends(get_supabase_auth_service),
) -> OAuthUrlResponse:
    """Generate an OAuth login URL for a provider."""

    oauth_data = await supabase_auth_service.get_oauth_url(
        provider=request.provider,
        redirect_uri=request.redirect_uri,
        state=request.state,
    )
    return OAuthUrlResponse(url=oauth_data["url"], state=oauth_data["state"])


@router.post("/oauth/callback", response_model=OAuthLoginResponse)
async def oauth_callback(
    request: OAuthCallbackRequest,
    response: Response,
    supabase_auth_service: SupabaseAuthService = Depends(get_supabase_auth_service),
    jwt_manager: JWTManager = Depends(get_jwt_manager),
) -> OAuthLoginResponse:
    """Handle OAuth callback and return JWT tokens."""
    user, _, is_new_user = await supabase_auth_service.oauth_callback(
        provider=request.provider,
        code=request.code,
        redirect_uri=request.redirect_uri,
        state=request.state,
    )

    access_token = jwt_manager.create_access_token(
        subject=str(user.id),
        scopes=user.permissions or [],
    )
    refresh_token = jwt_manager.create_refresh_token(subject=str(user.id))

    _set_refresh_cookie(response, refresh_token, jwt_manager)

    return OAuthLoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=jwt_manager.access_token_expire_minutes * 60,
        user=UserResponse.from_user(user),
        is_new_user=is_new_user,
    )


# Compatibility exports (tests patch legacy module path)
get_jwt_manager_dependency = get_jwt_manager
SupabaseAuthServiceDependency = SupabaseAuthService
UserServiceDependency = UserService


def _set_refresh_cookie(response: Response, token: str, jwt_manager: JWTManager) -> None:
    """Persist refresh token as an HTTPOnly cookie."""

    settings = get_settings()
    max_age = jwt_manager.refresh_token_expire_days * 24 * 60 * 60
    response.set_cookie(
        key="refresh_token",
        value=token,
        max_age=max_age,
        httponly=True,
        secure=settings.app_env.lower() in {"production", "staging"},
        samesite="lax",
        path="/",
    )


def _clear_refresh_cookie(response: Response) -> None:
    """Remove refresh token cookie."""

    response.delete_cookie(key="refresh_token", path="/")


__all__ = [
    "router",
    "register",
    "login",
    "refresh_token",
    "verify_token",
    "logout",
    "request_password_reset",
    "get_oauth_url",
    "get_current_user_info",
    "verify_email",
    "oauth_callback",
    "get_jwt_manager_dependency",
    "SupabaseAuthServiceDependency",
    "UserServiceDependency",
]
