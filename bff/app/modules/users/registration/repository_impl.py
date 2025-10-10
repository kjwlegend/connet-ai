"""SQLAlchemy implementation for registration sources."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.registration.models import UserRegistrationSourceModel
from app.modules.users.registration.repository import (
    UserRegistrationSourceRepositoryProtocol,
)


class UserRegistrationSourceRepository(UserRegistrationSourceRepositoryProtocol):
    """Persistence logic for registration source records."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_user(
        self, user_id: UUID
    ) -> Optional[UserRegistrationSourceModel]:
        stmt = select(UserRegistrationSourceModel).where(
            UserRegistrationSourceModel.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self, record: UserRegistrationSourceModel
    ) -> UserRegistrationSourceModel:
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def save(
        self, record: UserRegistrationSourceModel
    ) -> UserRegistrationSourceModel:
        await self.session.flush()
        await self.session.refresh(record)
        return record


__all__ = ["UserRegistrationSourceRepository"]
