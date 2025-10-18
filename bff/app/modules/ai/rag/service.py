"""RAG service for document processing and semantic search."""

from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, or_, select

from app.modules.ai.rag.models import RAGDocumentModel
from app.modules.ai.rag.repository import RAGDocumentRepositoryProtocol
from app.modules.ai.rag.schemas import RAGDocumentCreate, RAGDocumentResponse


class RAGService:
    """Coordinates RAG document processing and retrieval."""

    def __init__(
        self,
        rag_document_repository: RAGDocumentRepositoryProtocol,
    ) -> None:
        self.rag_document_repository = rag_document_repository

        self.document_processors: Dict[str, DocumentProcessor] = {
            "pdf": PDFProcessor(),
            "docx": DocxProcessor(),
            "txt": TextProcessor(),
            "md": MarkdownProcessor(),
            "html": HTMLProcessor(),
        }
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

    async def process_document(self, document_id: UUID) -> bool:
        document = await self.rag_document_repository.get_by_id(document_id)
        if not document:
            return False
        asyncio.create_task(self._process_document_async(document_id))
        return True

    async def semantic_search(
        self,
        query: str,
        document_ids: Optional[List[UUID]] = None,
        top_k: int = 10,
        search_type: str = "hybrid",
    ) -> List[Dict[str, Any]]:
        start_time = time.time()
        if search_type == "vector":
            results = await self._vector_search(query, document_ids, top_k)
        elif search_type == "keyword":
            results = await self._keyword_search(query, document_ids, top_k)
        else:
            results = await self._hybrid_search(query, document_ids, top_k)
        duration = time.time() - start_time
        for result in results:
            result.update({"search_time": duration, "search_type": search_type})
        return results

    async def delete_document_embeddings(self, document_id: UUID) -> bool:
        try:
            await self._delete_document_from_vector_store(document_id)
            return True
        except Exception as exc:  # pragma: no cover - defensive logging
            print(f"Error deleting embeddings for {document_id}: {exc}")
            return False

    async def get_document_chunks(
        self, document_id: UUID, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        chunks = await self.rag_document_repository.get_document_chunks(document_id)
        if limit:
            chunks = chunks[:limit]
        return [
            {
                "id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "metadata": chunk.chunk_agent_metadata,
                "quality_score": chunk.quality_score,
                "token_count": chunk.token_count,
                "section_title": chunk.section_title,
                "page_number": chunk.page_number,
            }
            for chunk in chunks
        ]

    async def get_document_processing_status(
        self, document_id: UUID
    ) -> Optional[Dict[str, Any]]:
        document = await self.rag_document_repository.get_by_id(document_id)
        if not document:
            return None
        return {
            "document_id": document.id,
            "processing_status": document.processing_status,
            "chunk_count": document.chunk_count,
            "quality_score": document.quality_score,
            "processed_at": document.processed_at,
        }

    async def reprocess_document(self, document_id: UUID) -> bool:
        document = await self.rag_document_repository.get_by_id(document_id)
        if not document:
            return False
        await self.rag_document_repository.update_processing_status(document_id, "pending")
        asyncio.create_task(self._process_document_async(document_id))
        return True

    async def create_rag_document(
        self, user_id: UUID, payload: RAGDocumentCreate
    ) -> RAGDocumentResponse:
        document = RAGDocumentModel.from_create_payload(payload, owner_id=user_id)
        created = await self.rag_document_repository.create(document)
        return RAGDocumentResponse.model_validate(created)

    async def get_user_rag_documents(
        self,
        user_id: UUID,
        file_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[RAGDocumentResponse]:
        documents = await self.rag_document_repository.get_by_owner(user_id)
        if file_type:
            documents = [doc for doc in documents if doc.file_type == file_type]
        return [
            RAGDocumentResponse.model_validate(doc)
            for doc in documents[skip : skip + limit]
        ]

    async def get_rag_document(
        self, document_id: UUID, user_id: UUID
    ) -> Optional[RAGDocumentResponse]:
        document = await self.rag_document_repository.get_by_id(document_id)
        if not document or document.owner_id != user_id:
            return None
        return RAGDocumentResponse.model_validate(document)

    async def delete_rag_document(self, document_id: UUID, user_id: UUID) -> bool:
        document = await self.rag_document_repository.get_by_id(document_id)
        if not document or document.owner_id != user_id:
            return False
        return await self.rag_document_repository.delete(document_id)

    async def _process_document_async(self, document_id: UUID) -> None:
        try:
            await self.rag_document_repository.update_processing_status(
                document_id, "processing"
            )
            document = await self.rag_document_repository.get_by_id(document_id)
            if not document:
                return
            processor = self.document_processors.get(document.file_type)
            if not processor:
                await self.rag_document_repository.update_processing_status(
                    document_id, "failed"
                )
                return
            processed = await processor.process(
                document.content, document.agent_metadata
            )
            chunks = await self._split_document_into_chunks(document, processed)
            embedded_chunks = await self._generate_chunk_embeddings(chunks)
            chunk_records = [
                {
                    "document_id": document_id,
                    "chunk_index": idx,
                    "content": chunk["content"],
                    "chunk_agent_metadata": chunk["metadata"],
                    "start_position": chunk.get("start_position", 0),
                    "end_position": chunk.get("end_position", 0),
                    "page_number": chunk.get("page_number"),
                    "section_title": chunk.get("section_title"),
                    "embedding_model": chunk["embedding_model"],
                    "embedding_dimension": len(chunk["embedding"]),
                    "quality_score": chunk["quality_score"],
                    "token_count": chunk["token_count"],
                    "created_at": datetime.utcnow(),
                }
                for idx, chunk in enumerate(embedded_chunks)
            ]
            stored_chunks = await self.rag_document_repository.create_chunks(
                chunk_records
            )
            await self._store_chunks_in_vector_store(stored_chunks, embedded_chunks)
            avg_quality = sum(chunk["quality_score"] for chunk in embedded_chunks) / len(
                embedded_chunks
            )
            await self.rag_document_repository.update_processing_status(
                document_id,
                "completed",
                chunk_count=len(chunks),
                quality_score=avg_quality,
            )
        except Exception as exc:  # pragma: no cover - defensive logging
            await self.rag_document_repository.update_processing_status(
                document_id, "failed"
            )
            print(f"Document processing failed for {document_id}: {exc}")

    async def _split_document_into_chunks(
        self,
        document,
        processed_content: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        chunks: List[Dict[str, Any]] = []
        content = processed_content["content"]
        chunk_size = 512
        words = content.split()
        estimated_tokens = len(words) * 1.3
        if estimated_tokens <= chunk_size:
            chunks.append(
                {
                    "content": content,
                    "metadata": processed_content.get("metadata", {}),
                    "start_position": 0,
                    "end_position": len(content),
                    "quality_score": self._calculate_chunk_quality(content),
                    "token_count": int(estimated_tokens),
                }
            )
            return chunks

        sentences = content.split(". ")
        current_chunk = ""
        current_tokens = 0
        start_position = 0
        for sentence in sentences:
            sentence_tokens = len(sentence.split()) * 1.3
            if current_tokens + sentence_tokens > chunk_size and current_chunk:
                chunks.append(
                    {
                        "content": current_chunk.strip(),
                        "metadata": processed_content.get("metadata", {}),
                        "start_position": start_position,
                        "end_position": start_position + len(current_chunk),
                        "quality_score": self._calculate_chunk_quality(
                            current_chunk
                        ),
                        "token_count": int(current_tokens),
                    }
                )
                overlap_content = (
                    ". ".join(current_chunk.split(". ")[-2:])
                    if ". " in current_chunk
                    else ""
                )
                start_position += len(current_chunk) - len(overlap_content)
                current_chunk = overlap_content + ". " + sentence
                current_tokens = len(overlap_content.split()) * 1.3 + sentence_tokens
            else:
                current_chunk += ". " + sentence if current_chunk else sentence
                current_tokens += sentence_tokens

        if current_chunk:
            chunks.append(
                {
                    "content": current_chunk.strip(),
                    "metadata": processed_content.get("metadata", {}),
                    "start_position": start_position,
                    "end_position": start_position + len(current_chunk),
                    "quality_score": self._calculate_chunk_quality(current_chunk),
                    "token_count": int(current_tokens),
                }
            )
        return chunks

    async def _generate_chunk_embeddings(
        self, chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        embedded_chunks: List[Dict[str, Any]] = []
        for chunk in chunks:
            embedding = await self.embedding_service.embed_text(chunk["content"])
            embedded_chunk = {
                **chunk,
                "embedding": embedding,
                "embedding_model": self.embedding_service.model_name,
            }
            embedded_chunks.append(embedded_chunk)
        return embedded_chunks

    async def _store_chunks_in_vector_store(
        self, stored_chunks: List[Any], embedded_chunks: List[Dict[str, Any]]
    ) -> None:
        for stored_chunk, embedded_chunk in zip(stored_chunks, embedded_chunks):
            await self.vector_store.store(
                id=str(stored_chunk.id),
                vector=embedded_chunk["embedding"],
                metadata={
                    "document_id": str(stored_chunk.document_id),
                    "chunk_index": stored_chunk.chunk_index,
                    "content": stored_chunk.content,
                    "quality_score": stored_chunk.quality_score,
                },
            )

    async def _vector_search(
        self,
        query: str,
        document_ids: Optional[List[UUID]] = None,
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        query_embedding = await self.embedding_service.embed_text(query)
        filters = {}
        if document_ids:
            filters["document_id"] = [str(doc_id) for doc_id in document_ids]
        vector_results = await self.vector_store.search(
            query_vector=query_embedding,
            top_k=top_k,
            filters=filters,
        )
        chunk_ids = [UUID(result["id"]) for result in vector_results]
        chunks = await self.rag_document_repository.get_chunks_by_ids(chunk_ids)
        results: List[Dict[str, Any]] = []
        for chunk in chunks:
            match = next(
                (item for item in vector_results if item["id"] == str(chunk.id)),
                None,
            )
            score = match["score"] if match else 0.0
            document = await self.rag_document_repository.get_by_id(chunk.document_id)
            if not document:
                continue
            results.append(
                {
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "content": chunk.content,
                    "metadata": chunk.chunk_agent_metadata,
                    "relevance_score": score,
                    "document_name": document.name,
                    "section_title": chunk.section_title,
                    "page_number": chunk.page_number,
                }
            )
        return results

    async def _keyword_search(
        self,
        query: str,
        document_ids: Optional[List[UUID]] = None,
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        conditions = [
            or_(
                RAGDocumentModel.name.ilike(f"%{query}%"),
                RAGDocumentModel.content.ilike(f"%{query}%"),
            )
        ]
        if document_ids:
            conditions.append(RAGDocumentModel.id.in_(document_ids))
        stmt = (
            select(RAGDocumentModel)
            .where(and_(*conditions))
            .order_by(RAGDocumentModel.quality_score.desc())
            .limit(top_k)
        )
        result = await self.rag_document_repository.session.execute(stmt)
        documents = result.scalars().all()
        return [
            {
                "document_id": doc.id,
                "document_name": doc.name,
                "content": doc.content,
                "relevance_score": doc.quality_score,
                "metadata": doc.agent_metadata,
            }
            for doc in documents
        ]

    async def _hybrid_search(
        self,
        query: str,
        document_ids: Optional[List[UUID]] = None,
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        vector_results = await self._vector_search(query, document_ids, top_k)
        keyword_results = await self._keyword_search(query, document_ids, top_k)
        combined = {result["chunk_id"]: result for result in vector_results}
        for item in keyword_results:
            chunk_id = item.get("chunk_id") or item["document_id"]
            combined.setdefault(chunk_id, item)
        return list(combined.values())[:top_k]

    async def _delete_document_from_vector_store(self, document_id: UUID) -> None:
        await self.vector_store.delete_namespace(str(document_id))

    def _calculate_chunk_quality(self, content: str) -> float:
        length_score = min(len(content) / 512, 1.0)
        structure_bonus = 0.1 if "\n" in content or "- " in content else 0.0
        return min(length_score + structure_bonus, 1.0)


class DocumentProcessor:
    async def process(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class PDFProcessor(DocumentProcessor):
    async def process(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0)
        return {"content": content, "metadata": metadata}


class DocxProcessor(DocumentProcessor):
    async def process(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0)
        return {"content": content, "metadata": metadata}


class TextProcessor(DocumentProcessor):
    async def process(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        return {"content": content, "metadata": metadata}


class MarkdownProcessor(DocumentProcessor):
    async def process(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        return {"content": content, "metadata": metadata}


class HTMLProcessor(DocumentProcessor):
    async def process(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        return {"content": content, "metadata": metadata}


class EmbeddingService:
    model_name = "text-embedding-3-large"

    async def embed_text(self, text: str) -> List[float]:
        await asyncio.sleep(0)
        return [0.0] * 1536


class VectorStore:
    async def store(self, id: str, vector: List[float], metadata: Dict[str, Any]) -> None:
        await asyncio.sleep(0)

    async def search(
        self,
        query_vector: List[float],
        top_k: int,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        await asyncio.sleep(0)
        return []

    async def delete_namespace(self, namespace: str) -> None:
        await asyncio.sleep(0)


__all__ = ["RAGService"]
