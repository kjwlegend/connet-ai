"""Repository protocol for user prompt library entries."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.modules.users.prompt_library.models import UserPromptLibraryModel


class UserPromptLibraryRepositoryProtocol(ABC):
    """Abstract operations for prompt library persistence."""

    @abstractmethod
    async def list_for_user(
        self, user_id: UUID
    ) -> List[UserPromptLibraryModel]: ...

    @abstractmethod
    async def get(
        self, prompt_id: UUID
    ) -> Optional[UserPromptLibraryModel]: ...

    @abstractmethod
    async def create(
        self, prompt: UserPromptLibraryModel
    ) -> UserPromptLibraryModel: ...

    @abstractmethod
    async def save(
        self, prompt: UserPromptLibraryModel
    ) -> UserPromptLibraryModel: ...

    @abstractmethod
    async def delete(self, prompt: UserPromptLibraryModel) -> None: ...


UserPromptLibraryRepository = UserPromptLibraryRepositoryProtocol

__all__ = [
    "UserPromptLibraryRepositoryProtocol",
    "UserPromptLibraryRepository",
]
