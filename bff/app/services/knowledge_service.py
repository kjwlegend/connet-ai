"""Backward-compatible shim for knowledge service."""

from app.modules.ai.knowledge_bases.repository_impl import KnowledgeBaseRepository
from app.modules.ai.rag.repository_impl import RAGDocumentRepository
from app.modules.ai.knowledge_bases.service import KnowledgeService as ModuleKnowledgeService


class KnowledgeService(ModuleKnowledgeService):
    """Compatibility wrapper preserving legacy constructor signature."""

    def __init__(self, session):
        knowledge_repo = KnowledgeBaseRepository(session)
        rag_repo = RAGDocumentRepository(session)
        super().__init__(
            knowledge_repository=knowledge_repo,
            rag_document_repository=rag_repo,
        )


__all__ = ["KnowledgeService"]
