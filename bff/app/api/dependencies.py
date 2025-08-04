"""
API Dependencies

This module contains dependency injection functions for FastAPI endpoints.
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config.settings import get_settings
from app.core.interfaces.repositories.user_repository import UserRepository
from app.infrastructure.cache.cache_manager import CacheManager, get_cache_manager
from app.infrastructure.database.connection import get_session
from app.infrastructure.database.repositories.user_repository_impl import (
    UserRepositoryImpl,
)
from app.infrastructure.security.auth import JWTManager, get_jwt_manager
from app.infrastructure.security.permissions import (
    PermissionManager,
    get_permission_manager,
)
from app.schemas.user import User
from app.services.user_service import UserService

# Security scheme
security = HTTPBearer(auto_error=False)


async def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> UserRepository:
    """Get user repository dependency."""
    return UserRepositoryImpl(session)


async def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    cache_manager: CacheManager = Depends(get_cache_manager),
) -> UserService:
    """Get user service dependency."""
    return UserService(user_repository=user_repo, cache_manager=cache_manager)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    jwt_manager: JWTManager = Depends(get_jwt_manager),
    user_service: UserService = Depends(get_user_service),
) -> User:
    """Get current authenticated user."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Verify JWT token
        payload = jwt_manager.verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
            )
        
        # Check token type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        
        # Get user from database
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user (alias for clarity)."""
    return current_user


def require_permission(resource: str, action: str):
    """Dependency factory for permission checking."""
    
    async def permission_dependency(
        current_user: User = Depends(get_current_user),
        permission_manager: PermissionManager = Depends(get_permission_manager),
    ) -> User:
        """Check if current user has required permission."""
        has_permission = await permission_manager.check_permission(
            user_id=current_user.id,
            resource=resource,
            action=action,
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions for {resource}:{action}",
            )
        
        return current_user
    
    return permission_dependency


def require_role(role_name: str):
    """Dependency factory for role checking."""
    
    async def role_dependency(
        current_user: User = Depends(get_current_user),
    ) -> User:
        """Check if current user has required role."""
        user_roles = getattr(current_user, 'roles', [])
        
        if role_name not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role_name}' required",
            )
        
        return current_user
    
    return role_dependency


async def get_pagination_params(
    page: int = 1,
    size: int = 20,
    max_size: int = 100,
) -> dict:
    """Get pagination parameters."""
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page must be >= 1",
        )
    
    if size < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Size must be >= 1",
        )
    
    if size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Size must be <= {max_size}",
        )
    
    offset = (page - 1) * size
    
    return {
        "page": page,
        "size": size,
        "offset": offset,
        "limit": size,
    }


async def get_settings_dependency():
    """Get settings dependency."""
    return get_settings()