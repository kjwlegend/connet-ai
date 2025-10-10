"""SQLAlchemy implementation for user LLM settings."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.llm_settings.models import UserLLMSettingsModel
from app.modules.users.llm_settings.repository import (
    UserLLMSettingsRepositoryProtocol,
)


class UserLLMSettingsRepository(UserLLMSettingsRepositoryProtocol):
    """Persistence logic for user LLM preferences."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_user(
        self, user_id: UUID
    ) -> Optional[UserLLMSettingsModel]:
        stmt = select(UserLLMSettingsModel).where(UserLLMSettingsModel.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self, settings: UserLLMSettingsModel
    ) -> UserLLMSettingsModel:
        self.session.add(settings)
        await self.session.flush()
        await self.session.refresh(settings)
        return settings

    async def save(
        self, settings: UserLLMSettingsModel
    ) -> UserLLMSettingsModel:
        await self.session.flush()
        await self.session.refresh(settings)
        return settings


__all__ = ["UserLLMSettingsRepository"]
