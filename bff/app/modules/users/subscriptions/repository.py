"""Repository protocol for user subscriptions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.modules.users.subscriptions.models import UserSubscriptionModel


class UserSubscriptionRepositoryProtocol(ABC):
    """Abstract operations for subscription persistence."""

    @abstractmethod
    async def get_active_by_user(
        self, user_id: UUID
    ) -> Optional[UserSubscriptionModel]: ...

    @abstractmethod
    async def save(
        self, subscription: UserSubscriptionModel
    ) -> UserSubscriptionModel: ...

    @abstractmethod
    async def create(
        self, subscription: UserSubscriptionModel
    ) -> UserSubscriptionModel: ...


UserSubscriptionRepository = UserSubscriptionRepositoryProtocol

__all__ = [
    "UserSubscriptionRepositoryProtocol",
    "UserSubscriptionRepository",
]
