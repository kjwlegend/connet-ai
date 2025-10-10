"""Backward-compatible shim for the AI tools service."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.tools.repository_impl import (
    ToolRepository,
    WebhookRepository,
    WebhookTriggerRepository,
)
from app.modules.ai.tools.service import ToolsService as ModuleToolsService


class ToolsService(ModuleToolsService):
    """Compatibility wrapper preserving legacy constructor signature."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(
            tool_repository=ToolRepository(session),
            webhook_repository=WebhookRepository(session),
            webhook_trigger_repository=WebhookTriggerRepository(session),
        )


__all__ = ["ToolsService"]
