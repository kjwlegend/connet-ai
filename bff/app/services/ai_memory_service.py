"""Backward-compatible shim for AI memory service."""

from app.modules.ai.memory.repository_impl import (
    AIMemoryRepository,
    AIConversationSummaryRepository,
)
from app.modules.ai.memory.service import AIMemoryService as ModuleAIMemoryService


class AIMemoryService(ModuleAIMemoryService):
    """Compatibility wrapper that preserves legacy constructor signature."""

    def __init__(self, session):
        memory_repo = AIMemoryRepository(session)
        summary_repo = AIConversationSummaryRepository(session)
        super().__init__(memory_repo=memory_repo, summary_repository=summary_repo)


__all__ = ["AIMemoryService"]
