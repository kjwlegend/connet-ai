"""SQLAlchemy implementation for user prompt library."""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.prompt_library.models import UserPromptLibraryModel
from app.modules.users.prompt_library.repository import (
    UserPromptLibraryRepositoryProtocol,
)


class UserPromptLibraryRepository(UserPromptLibraryRepositoryProtocol):
    """Persistence logic for prompt entries."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_user(
        self, user_id: UUID
    ) -> List[UserPromptLibraryModel]:
        stmt = select(UserPromptLibraryModel).where(UserPromptLibraryModel.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get(
        self, prompt_id: UUID
    ) -> Optional[UserPromptLibraryModel]:
        return await self.session.get(UserPromptLibraryModel, prompt_id)

    async def create(
        self, prompt: UserPromptLibraryModel
    ) -> UserPromptLibraryModel:
        self.session.add(prompt)
        await self.session.flush()
        await self.session.refresh(prompt)
        return prompt

    async def save(
        self, prompt: UserPromptLibraryModel
    ) -> UserPromptLibraryModel:
        await self.session.flush()
        await self.session.refresh(prompt)
        return prompt

    async def delete(self, prompt: UserPromptLibraryModel) -> None:
        await self.session.delete(prompt)
        await self.session.flush()


__all__ = ["UserPromptLibraryRepository"]
