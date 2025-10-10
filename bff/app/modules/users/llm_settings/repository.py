"""Repository protocol for user LLM settings."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.modules.users.llm_settings.models import UserLLMSettingsModel


class UserLLMSettingsRepositoryProtocol(ABC):
    """Abstract operations for LLM settings persistence."""

    @abstractmethod
    async def get_by_user(
        self, user_id: UUID
    ) -> Optional[UserLLMSettingsModel]: ...

    @abstractmethod
    async def save(
        self, settings: UserLLMSettingsModel
    ) -> UserLLMSettingsModel: ...

    @abstractmethod
    async def create(
        self, settings: UserLLMSettingsModel
    ) -> UserLLMSettingsModel: ...


UserLLMSettingsRepository = UserLLMSettingsRepositoryProtocol

__all__ = [
    "UserLLMSettingsRepositoryProtocol",
    "UserLLMSettingsRepository",
]
