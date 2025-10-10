"""SQLModel definitions for user subscriptions."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class UserSubscriptionModel(SQLModel, table=True):
    """User membership/subscription state."""

    __tablename__ = "user_subscriptions"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)

    plan_type: str = Field(max_length=20, index=True)
    plan_name: str = Field(max_length=50)
    plan_price: Decimal = Field(decimal_places=2, max_digits=12)

    status: str = Field(default="active", max_length=20, index=True)
    billing_cycle: str = Field(default="monthly", max_length=20)
    current_period_start: datetime = Field()
    current_period_end: datetime = Field()

    monthly_message_limit: int = Field(default=1000)
    monthly_ai_token_limit: int = Field(default=50000)
    max_file_storage_gb: int = Field(default=1)
    max_conversation_history_days: int = Field(default=30)

    features_enabled: dict = Field(default_factory=dict, sa_column=Column(JSON))

    payment_method: Optional[str] = Field(default=None, max_length=50)
    external_subscription_id: Optional[str] = Field(default=None, max_length=200)
    cancel_at_period_end: bool = Field(default=False)
    canceled_at: Optional[datetime] = Field(default=None)

    trial_start: Optional[datetime] = Field(default=None)
    trial_end: Optional[datetime] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


__all__ = ["UserSubscriptionModel"]
