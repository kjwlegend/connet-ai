"""Lightweight settings service placeholder."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4
import secrets
import string


class SettingsService:
    """Temporary in-memory implementation for settings endpoints."""

    def __init__(self) -> None:
        self._prompt_store: Dict[UUID, List[Dict]] = {}
        self._invite_stats: Dict[UUID, Dict] = {}
        self._order_history: Dict[UUID, List[Dict]] = {}
        self._account_settings: Dict[UUID, Dict] = {}

    async def get_user_subscription(self, user_id: UUID) -> Dict:
        return {
            "plan": "basic",
            "status": "active",
            "current_period_end": datetime.utcnow(),
            "cancel_at_period_end": False,
            "payment_method": None,
        }

    async def upgrade_subscription(
        self,
        user_id: UUID,
        plan_type: str,
        billing_cycle: str,
    ) -> Dict:
        return {
            "message": "Subscription upgrade scheduled",
            "plan": plan_type,
            "billing_cycle": billing_cycle,
        }

    async def cancel_subscription(
        self,
        user_id: UUID,
        cancel_at_period_end: bool,
    ) -> None:
        return None

    async def get_llm_settings(self, user_id: UUID) -> Dict:
        return {
            "user_id": user_id,
            "default_provider": "openai",
            "default_model": "gpt-4",
            "provider_configs": {},
            "auto_select_model": True,
        }

    async def update_llm_settings(self, user_id: UUID, settings_data: Dict) -> Dict:
        return {**await self.get_llm_settings(user_id), **settings_data}

    async def test_provider_api_key(self, provider: str, api_key: str) -> bool:
        return bool(provider and api_key)

    async def get_user_prompts(
        self,
        user_id: UUID,
        skip: int,
        limit: int,
        category: Optional[str],
        search: Optional[str],
        favorites_only: bool,
    ) -> List[Dict]:
        prompts = self._prompt_store.get(user_id, [])
        return prompts[skip : skip + limit]

    async def create_prompt(self, user_id: UUID, prompt_data: Dict) -> Dict:
        prompt = {
            "id": uuid4(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            **prompt_data,
        }
        self._prompt_store.setdefault(user_id, []).append(prompt)
        return prompt

    async def get_prompt(self, user_id: UUID, prompt_id: UUID) -> Optional[Dict]:
        for prompt in self._prompt_store.get(user_id, []):
            if prompt["id"] == prompt_id:
                return prompt
        return None

    async def update_prompt(
        self,
        user_id: UUID,
        prompt_id: UUID,
        prompt_data: Dict,
    ) -> Optional[Dict]:
        prompts = self._prompt_store.get(user_id, [])
        for idx, prompt in enumerate(prompts):
            if prompt["id"] == prompt_id:
                prompts[idx] = {**prompt, **prompt_data, "updated_at": datetime.utcnow()}
                return prompts[idx]
        return None

    async def delete_prompt(self, user_id: UUID, prompt_id: UUID) -> bool:
        prompts = self._prompt_store.get(user_id, [])
        filtered = [prompt for prompt in prompts if prompt["id"] != prompt_id]
        removed = len(filtered) != len(prompts)
        self._prompt_store[user_id] = filtered
        return removed

    async def toggle_favorite_prompt(
        self,
        user_id: UUID,
        prompt_id: UUID,
        is_favorite: bool,
    ) -> Optional[Dict]:
        prompt = await self.get_prompt(user_id, prompt_id)
        if prompt:
            prompt["is_favorite"] = is_favorite
            prompt["updated_at"] = datetime.utcnow()
        return prompt

    async def get_invite_stats(self, user_id: UUID) -> Dict:
        return self._invite_stats.get(
            user_id,
            {
                "invite_code": None,
                "total_sent": 0,
                "accepted": 0,
                "pending": 0,
                "rewards_earned": 0.0,
                "currency": "USD",
            },
        )

    async def generate_invite_code(self, user_id: UUID) -> Dict:
        code = "".join(secrets.choice(string.ascii_uppercase) for _ in range(6))
        stats = await self.get_invite_stats(user_id)
        stats["invite_code"] = code
        self._invite_stats[user_id] = stats
        return {"invite_code": code}

    async def get_invite_history(
        self,
        user_id: UUID,
        skip: int,
        limit: int,
    ) -> List[Dict]:
        return []

    async def get_order_history(
        self,
        user_id: UUID,
        skip: int,
        limit: int,
    ) -> List[Dict]:
        return self._order_history.get(user_id, [])[skip : skip + limit]

    async def get_account_settings(self, user_id: UUID) -> Dict:
        return self._account_settings.get(user_id, {})

    async def update_account_settings(
        self,
        user_id: UUID,
        settings_data: Dict,
    ) -> Dict:
        merged = {**self._account_settings.get(user_id, {}), **settings_data}
        self._account_settings[user_id] = merged
        return merged

    async def export_user_data(self, user_id: UUID) -> Dict:
        return {
            "user_id": user_id,
            "status": "scheduled",
            "requested_at": datetime.utcnow(),
        }

    async def delete_user_account(self, user_id: UUID) -> None:
        self._prompt_store.pop(user_id, None)
        self._invite_stats.pop(user_id, None)
        self._order_history.pop(user_id, None)
        self._account_settings.pop(user_id, None)


__all__ = ["SettingsService"]
