"""Business logic for user registration source tracking."""

from __future__ import annotations

from typing import Any, Dict, Optional
from uuid import UUID

from app.modules.users.registration.models import UserRegistrationSourceModel
from app.modules.users.registration.repository import (
    UserRegistrationSourceRepositoryProtocol,
)


class UserRegistrationSourceService:
    """Records and retrieves registration metadata."""

    def __init__(
        self, repository: UserRegistrationSourceRepositoryProtocol
    ) -> None:
        self.repository = repository

    async def get_record(
        self, user_id: UUID
    ) -> Optional[UserRegistrationSourceModel]:
        return await self.repository.get_by_user(user_id)

    async def record_source(
        self,
        user_id: UUID,
        data: Dict[str, Any],
    ) -> UserRegistrationSourceModel:
        record = await self.repository.get_by_user(user_id)
        if record is None:
            record = UserRegistrationSourceModel(user_id=user_id, **data)
            return await self.repository.create(record)

        for key, value in data.items():
            if hasattr(record, key):
                setattr(record, key, value)
        return await self.repository.save(record)


__all__ = ["UserRegistrationSourceService"]
