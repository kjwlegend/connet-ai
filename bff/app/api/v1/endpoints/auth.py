"""
Authentication Endpoints

This module contains authentication and authorization endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.api.dependencies import get_current_user, get_user_service, security
from app.infrastructure.security.auth import JWTManager, get_jwt_manager
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenVerifyRequest,
    UserResponse,
)
from app.services.auth_service import AuthService, get_auth_service
from app.services.user_service import UserService
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Register a new user."""
    try:
        user = await auth_service.register_user(
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            username=request.username,
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
    auth_service: AuthService = Depends(get_auth_service),
    jwt_manager: JWTManager = Depends(get_jwt_manager),
) -> LoginResponse:
    """Authenticate user and return JWT tokens."""
    try:
        # Authenticate user
        user = await auth_service.authenticate_user(
            email=request.email,
            password=request.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Generate tokens
        access_token = jwt_manager.create_access_token(
            subject=user.id,
            scopes=user.permissions or []
        )
        refresh_token = jwt_manager.create_refresh_token(subject=user.id)
        
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
            subject=user.id,
            scopes=user.permissions or []
        )
        new_refresh_token = jwt_manager.create_refresh_token(subject=user.id)
        
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