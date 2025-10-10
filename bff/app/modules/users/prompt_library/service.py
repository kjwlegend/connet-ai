"""Business logic for user prompt library."""

from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import HTTPException, status

from app.modules.users.prompt_library.models import UserPromptLibraryModel
from app.modules.users.prompt_library.repository import (
    UserPromptLibraryRepositoryProtocol,
)


class UserPromptLibraryService:
    """Manages CRUD for saved prompts."""

    def __init__(self, repository: UserPromptLibraryRepositoryProtocol) -> None:
        self.repository = repository

    async def list_prompts(self, user_id: UUID) -> List[UserPromptLibraryModel]:
        return await self.repository.list_for_user(user_id)

    async def create_prompt(
        self,
        user_id: UUID,
        title: str,
        prompt_text: str,
        description: str | None = None,
        category: str = "general",
    ) -> UserPromptLibraryModel:
        prompt = UserPromptLibraryModel(
            user_id=user_id,
            title=title,
            prompt_text=prompt_text,
            description=description,
            category=category,
        )
        return await self.repository.create(prompt)

    async def delete_prompt(self, prompt_id: UUID) -> None:
        prompt = await self.repository.get(prompt_id)
        if not prompt:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
        await self.repository.delete(prompt)


__all__ = ["UserPromptLibraryService"]
