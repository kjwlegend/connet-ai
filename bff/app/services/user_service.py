"""Backward-compatible shim for user service in the new modules layout."""

from app.modules.users.service import UserService


async def get_user_service(*args, **kwargs):  # pragma: no cover - compatibility shim
    from app.api.deps.services import get_user_service as _dep_get_user_service

    return await _dep_get_user_service(*args, **kwargs)


__all__ = ["UserService", "get_user_service"]
