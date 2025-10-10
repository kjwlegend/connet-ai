"""Backward-compatible shim for RAG service."""

from app.modules.ai.rag.repository_impl import RAGDocumentRepository
from app.modules.ai.rag.service import RAGService as ModuleRAGService


class RAGService(ModuleRAGService):
    """Compatibility wrapper preserving legacy constructor signature."""

    def __init__(self, session):
        repository = RAGDocumentRepository(session)
        super().__init__(rag_document_repository=repository)


__all__ = ["RAGService"]
