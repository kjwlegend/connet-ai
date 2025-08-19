"""
Authentication Endpoints

This module contains authentication and authorization endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.api.dependencies import get_current_user, get_user_service, get_supabase_auth_service, security
from app.infrastructure.security.auth import JWTManager, get_jwt_manager
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenVerifyRequest,
    PasswordResetRequest,
    OAuthCallbackRequest,
    OAuthLoginResponse,
    OAuthUrlRequest,
    OAuthUrlResponse,
)
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService, get_auth_service
from app.services.supabase_auth_service import SupabaseAuthService
from app.services.user_service import UserService
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(
    request: RegisterRequest,
    supabase_auth_service: SupabaseAuthService = Depends(get_supabase_auth_service),
) -> UserResponse:
    """Register a new user using Supabase Auth."""
    try:
        user, auth_response = await supabase_auth_service.register_user(
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
        
        logger.info(f"User registered successfully: {user.email}")
        return UserResponse.from_user(user)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    supabase_auth_service: SupabaseAuthService = Depends(get_supabase_auth_service),
    jwt_manager: JWTManager = Depends(get_jwt_manager),
) -> LoginResponse:
    """Authenticate user using Supabase Auth and return JWT tokens."""
    try:
        # Authenticate user with Supabase
        user, auth_response = await supabase_auth_service.login_user(
            email=request.email,
            password=request.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # We can either use Supabase session tokens or generate our own JWT
        # For now, let's use our own JWT system for consistency
        access_token = jwt_manager.create_access_token(
            subject=str(user.id),
            scopes=user.permissions or []
        )
        refresh_token = jwt_manager.create_refresh_token(subject=str(user.id))
        
        # Log token generation for debugging
        logger.debug(f"Generated access token for user {user.email}: {access_token[:20]}...")
        
        # Verify the token we just created
        try:
            test_payload = jwt_manager.verify_token(access_token)
            logger.debug(f"Token verification test successful: {test_payload.get('sub')}")
        except Exception as e:
            logger.error(f"Generated token failed verification: {e}")
        
        logger.info(f"User logged in successfully: {user.email}")
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=jwt_manager.access_token_expire_minutes * 60,
            user=UserResponse.from_user(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    jwt_manager: JWTManager = Depends(get_jwt_manager),
    user_service: UserService = Depends(get_user_service),
) -> LoginResponse:
    """Refresh access token using refresh token."""
    try:
        # Verify refresh token
        payload = jwt_manager.verify_token(request.refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Get user
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive"
            )
        
        # Generate new tokens
        access_token = jwt_manager.create_access_token(
            subject=str(user.id),
            scopes=user.permissions or []
        )
        new_refresh_token = jwt_manager.create_refresh_token(subject=str(user.id))
        
        logger.info(f"Token refreshed for user: {user.email}")
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=jwt_manager.access_token_expire_minutes * 60,
            user=UserResponse.from_user(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


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
                "scopes": payload.get("scopes", [])
            }
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    jwt_manager: JWTManager = Depends(get_jwt_manager),
) -> dict:
    """Logout user by blacklisting the token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        # In a production system, you would add the token to a blacklist
        # For now, we'll just validate it and return success
        jwt_manager.verify_token(credentials.credentials)
        
        # TODO: Add token to blacklist in Redis
        # await jwt_manager.blacklist_token(credentials.credentials)
        
        logger.info("User logged out successfully")
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user),
) -> UserResponse:
    """Get current user information."""
    return UserResponse.from_user(current_user)


@router.post("/password-reset")
async def request_password_reset(
    request: PasswordResetRequest,
    supabase_auth_service: SupabaseAuthService = Depends(get_supabase_auth_service),
) -> dict:
    """Request password reset email."""
    try:
        success = await supabase_auth_service.reset_password(
            email=request.email,
            redirect_to="http://localhost:3000/auth/reset-password"
        )
        
        if success:
            return {"message": "Password reset email sent successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to send password reset email"
            )
        
    except Exception as e:
        logger.error(f"Password reset failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )


@router.post("/verify-email")
async def verify_email(
    token: str,
    email: str,
    supabase_auth_service: SupabaseAuthService = Depends(get_supabase_auth_service),
) -> dict:
    """Verify user email address."""
    try:
        success = await supabase_auth_service.verify_email(token, email)
        
        if success:
            return {"message": "Email verified successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )
        
    except Exception as e:
        logger.error(f"Email verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email verification failed"
        )


@router.get("/oauth/url", response_model=OAuthUrlResponse)
async def get_oauth_url(
    request: OAuthUrlRequest = Depends(),
    supabase_auth_service: SupabaseAuthService = Depends(get_supabase_auth_service),
) -> OAuthUrlResponse:
    """Generate OAuth authorization URL for the specified provider."""
    try:
        # Validate provider
        if request.provider not in ["google", "github"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported OAuth provider. Supported providers: google, github"
            )
        
        # Generate OAuth URL
        oauth_data = await supabase_auth_service.get_oauth_url(
            provider=request.provider,
            redirect_uri=request.redirect_uri,
            state=request.state,
        )
        
        logger.info(f"Generated OAuth URL for provider: {request.provider}")
        
        return OAuthUrlResponse(
            url=oauth_data["url"],
            state=oauth_data["state"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate OAuth URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate OAuth URL"
        )


@router.post("/oauth/callback", response_model=OAuthLoginResponse)
async def oauth_callback(
    request: OAuthCallbackRequest,
    supabase_auth_service: SupabaseAuthService = Depends(get_supabase_auth_service),
    jwt_manager: JWTManager = Depends(get_jwt_manager),
) -> OAuthLoginResponse:
    """Handle OAuth callback and authenticate user."""
    try:
        # Validate provider
        if request.provider not in ["google", "github"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported OAuth provider"
            )
        
        # Exchange code for tokens and user data
        user, auth_response, is_new_user = await supabase_auth_service.oauth_callback(
            provider=request.provider,
            code=request.code,
            redirect_uri=request.redirect_uri,
            state=request.state,
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="OAuth authentication failed"
            )
        
        # Generate our own JWT tokens for consistency with email/password flow
        access_token = jwt_manager.create_access_token(
            subject=str(user.id),
            scopes=user.permissions or []
        )
        refresh_token = jwt_manager.create_refresh_token(subject=str(user.id))
        
        logger.info(f"OAuth authentication successful for user: {user.email} (provider: {request.provider})")
        
        return OAuthLoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=jwt_manager.access_token_expire_minutes * 60,
            user=UserResponse.from_user(user),
            is_new_user=is_new_user
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"OAuth callback failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth authentication failed"
        )