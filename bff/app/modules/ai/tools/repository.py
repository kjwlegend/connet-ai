"""Repository protocols for AI tools and webhooks."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from app.modules.ai.tools.models import (
    ToolModel,
    WebhookModel,
    WebhookTriggerModel,
)


class ToolRepositoryProtocol(ABC):
    """Abstract persistence operations for tools."""

    @abstractmethod
    async def get_by_id(self, tool_id: UUID) -> Optional[ToolModel]:
        ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[ToolModel]:
        ...

    @abstractmethod
    async def get_by_creator(self, creator_id: UUID) -> List[ToolModel]:
        ...

    @abstractmethod
    async def search_tools(
        self,
        *,
        query: str,
        tool_type: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        security_level: Optional[str] = None,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Tuple[List[ToolModel], int]:
        ...

    @abstractmethod
    async def get_popular_tools(self, limit: int = 10) -> List[ToolModel]:
        ...

    @abstractmethod
    async def get_recommended_tools(
        self, category: str, limit: int = 5
    ) -> List[ToolModel]:
        ...

    @abstractmethod
    async def create_tool(self, tool: ToolModel) -> ToolModel:
        ...

    @abstractmethod
    async def update_tool(self, tool: ToolModel) -> Optional[ToolModel]:
        ...

    @abstractmethod
    async def delete_tool(self, tool_id: UUID) -> bool:
        ...

    @abstractmethod
    async def increment_usage_count(self, tool_id: UUID) -> bool:
        ...

    @abstractmethod
    async def update_tool_stats(
        self, *, tool_id: UUID, success: bool, execution_time: float
    ) -> bool:
        ...


class WebhookRepositoryProtocol(ABC):
    """Abstract persistence operations for tool webhooks."""

    @abstractmethod
    async def get_by_id(self, webhook_id: UUID) -> Optional[WebhookModel]:
        ...

    @abstractmethod
    async def get_by_creator(self, creator_id: UUID) -> List[WebhookModel]:
        ...

    @abstractmethod
    async def get_active_webhooks(self) -> List[WebhookModel]:
        ...

    @abstractmethod
    async def get_webhooks_by_event_type(self, event_type: str) -> List[WebhookModel]:
        ...

    @abstractmethod
    async def create(self, webhook: WebhookModel) -> WebhookModel:
        ...

    @abstractmethod
    async def update(self, webhook: WebhookModel) -> Optional[WebhookModel]:
        ...

    @abstractmethod
    async def delete(self, webhook_id: UUID) -> bool:
        ...

    @abstractmethod
    async def update_webhook_stats(self, webhook_id: UUID, success: bool) -> bool:
        ...


class WebhookTriggerRepositoryProtocol(ABC):
    """Abstract persistence operations for webhook triggers."""

    @abstractmethod
    async def get_by_webhook(
        self, webhook_id: UUID, limit: int = 50
    ) -> List[WebhookTriggerModel]:
        ...

    @abstractmethod
    async def get_failed_triggers(
        self, webhook_id: UUID
    ) -> List[WebhookTriggerModel]:
        ...

    @abstractmethod
    async def create_trigger(
        self, trigger: WebhookTriggerModel
    ) -> WebhookTriggerModel:
        ...

    @abstractmethod
    async def update_trigger(
        self, trigger: WebhookTriggerModel
    ) -> Optional[WebhookTriggerModel]:
        ...

    @abstractmethod
    async def delete_trigger(self, trigger_id: UUID) -> bool:
        ...


__all__ = [
    "ToolRepositoryProtocol",
    "WebhookRepositoryProtocol",
    "WebhookTriggerRepositoryProtocol",
]
