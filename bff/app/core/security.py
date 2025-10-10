"""Security utilities shared across modules and API dependencies."""

from typing import Iterable


def check_roles(user_roles: Iterable[str], required_roles: Iterable[str]) -> bool:
    """Return True when all required roles exist in the user's role collection."""
    user_role_set = set(role for role in user_roles or [])
    return all(role in user_role_set for role in required_roles)


async def check_permissions(permission_manager, user_id: str, resource: str, action: str) -> bool:
    """Delegate permission evaluation to the configured permission manager."""
    return await permission_manager.check_permission(
        user_id=user_id,
        resource=resource,
        action=action,
    )


def require_roles(*roles: str):
    """Factory returning a predicate that enforces required roles."""

    required = set(roles)

    def predicate(user_roles: Iterable[str]) -> bool:
        return check_roles(user_roles, required)

    return predicate


__all__ = ["check_permissions", "check_roles", "require_roles"]
