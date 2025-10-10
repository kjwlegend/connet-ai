"""SQLAlchemy implementation for user subscriptions."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.subscriptions.models import UserSubscriptionModel
from app.modules.users.subscriptions.repository import (
    UserSubscriptionRepositoryProtocol,
)


class UserSubscriptionRepository(UserSubscriptionRepositoryProtocol):
    """Persistence logic for subscription records."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_active_by_user(
        self, user_id: UUID
    ) -> Optional[UserSubscriptionModel]:
        stmt = select(UserSubscriptionModel).where(
            UserSubscriptionModel.user_id == user_id,
            UserSubscriptionModel.status == "active",
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self, subscription: UserSubscriptionModel
    ) -> UserSubscriptionModel:
        self.session.add(subscription)
        await self.session.flush()
        await self.session.refresh(subscription)
        return subscription

    async def save(
        self, subscription: UserSubscriptionModel
    ) -> UserSubscriptionModel:
        await self.session.flush()
        await self.session.refresh(subscription)
        return subscription


__all__ = ["UserSubscriptionRepository"]
