"""Authentication dependencies for FastAPI routes."""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.modules.users.schemas import User
from app.modules.users.service import UserService
from app.services.supabase_auth_service import SupabaseAuthService
from app.infrastructure.security.auth import JWTManager, get_jwt_manager
from app.utils.logging import get_logger

from .services import get_supabase_auth_service, get_user_service

logger = get_logger(__name__)
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    jwt_manager: JWTManager = Depends(get_jwt_manager),
    user_service: UserService = Depends(get_user_service),
    supabase_auth_service: SupabaseAuthService = Depends(get_supabase_auth_service),
) -> User:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        token = credentials.credentials
        token_preview = token[:20] + "..." if len(token) > 20 else token
        logger.debug("Attempting to verify JWT", extra={"token": token_preview})

        try:
            payload = jwt_manager.verify_token(token)
            user_id = payload.get("sub")
            if not user_id:
                raise ValueError("Invalid token: missing subject")

            if payload.get("type") != "access":
                raise ValueError("Invalid token type")

            user = await user_service.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")

            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account is inactive",
                )

            return user

        except ValueError as exc:
            logger.warning("JWT verification failed", extra={"error": str(exc)})
            user = await supabase_auth_service.get_user_from_token(token)
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or inactive token",
                )
            return user

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {exc}",
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user


__all__ = ["get_current_user", "get_current_active_user", "security"]
