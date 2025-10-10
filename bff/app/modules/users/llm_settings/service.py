"""Business logic for user LLM settings."""

from __future__ import annotations

from typing import Any, Dict, Optional
from uuid import UUID

from app.modules.users.llm_settings.models import UserLLMSettingsModel
from app.modules.users.llm_settings.repository import (
    UserLLMSettingsRepositoryProtocol,
)


class UserLLMSettingsService:
    """Exposes helpers for reading/updating LLM preferences."""

    def __init__(self, repository: UserLLMSettingsRepositoryProtocol) -> None:
        self.repository = repository

    async def get_settings(self, user_id: UUID) -> Optional[UserLLMSettingsModel]:
        return await self.repository.get_by_user(user_id)

    async def upsert_settings(
        self,
        user_id: UUID,
        payload: Dict[str, Any],
    ) -> UserLLMSettingsModel:
        model = await self.repository.get_by_user(user_id)
        if model is None:
            model = UserLLMSettingsModel(user_id=user_id, **payload)
            return await self.repository.create(model)

        for key, value in payload.items():
            if hasattr(model, key):
                setattr(model, key, value)
        return await self.repository.save(model)


__all__ = ["UserLLMSettingsService"]
