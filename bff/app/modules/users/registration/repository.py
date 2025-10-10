"""Repository protocol for registration sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.modules.users.registration.models import UserRegistrationSourceModel


class UserRegistrationSourceRepositoryProtocol(ABC):
    """Abstract persistence operations for registration source records."""

    @abstractmethod
    async def get_by_user(
        self, user_id: UUID
    ) -> Optional[UserRegistrationSourceModel]: ...

    @abstractmethod
    async def create(
        self, record: UserRegistrationSourceModel
    ) -> UserRegistrationSourceModel: ...

    @abstractmethod
    async def save(
        self, record: UserRegistrationSourceModel
    ) -> UserRegistrationSourceModel: ...


UserRegistrationSourceRepository = UserRegistrationSourceRepositoryProtocol

__all__ = [
    "UserRegistrationSourceRepositoryProtocol",
    "UserRegistrationSourceRepository",
]
