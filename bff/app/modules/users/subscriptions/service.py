"""Business logic for user subscriptions."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status

from app.modules.users.subscriptions.models import UserSubscriptionModel
from app.modules.users.subscriptions.repository import (
    UserSubscriptionRepositoryProtocol,
)


class UserSubscriptionService:
    """Handles subscription lifecycle events."""

    def __init__(self, repository: UserSubscriptionRepositoryProtocol) -> None:
        self.repository = repository

    async def get_active_subscription(
        self, user_id: UUID
    ) -> Optional[UserSubscriptionModel]:
        return await self.repository.get_active_by_user(user_id)

    async def upsert_subscription(
        self,
        user_id: UUID,
        plan_type: str,
        plan_name: str,
        plan_price: Decimal,
        billing_cycle: str,
        period_start: datetime,
        period_end: datetime,
    ) -> UserSubscriptionModel:
        subscription = await self.repository.get_active_by_user(user_id)
        if subscription is None:
            subscription = UserSubscriptionModel(
                user_id=user_id,
                plan_type=plan_type,
                plan_name=plan_name,
                plan_price=plan_price,
                billing_cycle=billing_cycle,
                current_period_start=period_start,
                current_period_end=period_end,
            )
            return await self.repository.create(subscription)

        subscription.plan_type = plan_type
        subscription.plan_name = plan_name
        subscription.plan_price = plan_price
        subscription.billing_cycle = billing_cycle
        subscription.current_period_start = period_start
        subscription.current_period_end = period_end
        subscription.updated_at = datetime.utcnow()
        return await self.repository.save(subscription)

    async def cancel_subscription(self, user_id: UUID) -> None:
        subscription = await self.repository.get_active_by_user(user_id)
        if not subscription:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")
        subscription.status = "canceled"
        subscription.canceled_at = datetime.utcnow()
        await self.repository.save(subscription)


__all__ = ["UserSubscriptionService"]
