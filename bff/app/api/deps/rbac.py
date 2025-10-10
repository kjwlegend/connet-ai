"""RBAC/permission related dependencies."""

from fastapi import Depends, HTTPException, status

from app.core.security import check_permissions, require_roles as build_role_checker
from app.infrastructure.security.permissions import (
    PermissionManager,
    get_permission_manager,
)
from app.modules.users.schemas import User

from .auth import get_current_user


async def require_permission(
    resource: str,
    action: str,
    current_user: User = Depends(get_current_user),
    permission_manager: PermissionManager = Depends(get_permission_manager),
) -> User:
    has_permission = await check_permissions(
        permission_manager,
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


def require_roles(*roles: str):
    role_checker = build_role_checker(*roles)

    async def dependency(current_user: User = Depends(get_current_user)) -> User:
        if not role_checker(getattr(current_user, "roles", [])):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Roles {roles} required",
            )
        return current_user

    return dependency


__all__ = ["require_permission", "require_roles"]
