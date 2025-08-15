"""AI RAG service for document processing and semantic search."""

import asyncio
import json
import time
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID, uuid4

from app.infrastructure.database.repositories.ai_rag_repository_impl import (
    AIRAGDocumentRepositoryImpl,
    AIRAGDocumentChunkRepositoryImpl
)
from app.schemas.ai import (
    DocumentCreate,
    DocumentResponse,
    DocumentSearchRequest,
    DocumentSearchResult,
    DocumentSearchResponse,
    PaginationParams
)
from app.services.base import BaseService


class AIRAGService(BaseService):
    """AI RAG service for document processing and search"""
    
    def __init__(self, session):
        super().__init__(session)
        self.document_repo = AIRAGDocumentRepositoryImpl(session)
        self.chunk_repo = AIRAGDocumentChunkRepositoryImpl(session)
        
        # Document processors
        self.document_processors = {
            'pdf': PDFProcessor(),
            'docx': DocxProcessor(),
            'txt': TextProcessor(),
            'md': MarkdownProcessor(),
            'html': HTMLProcessor()
        }
        
        # Embedding service (placeholder)
        self.embedding_service = EmbeddingService()
        
        # Vector store (placeholder)
        self.vector_store = VectorStore()
    
    async def create_document(self, document_data: DocumentCreate, user_id: UUID) -> DocumentResponse:
        """Create and process a new document"""
        
        # Create document record
        document = await self.document_repo.create_document(document_data, user_id)
        
        # Process document asynchronously
        asyncio.create_task(self._process_document_async(document.id))
        
        return DocumentResponse.model_validate(document)
    
    async def get_document(self, document_id: UUID, user_id: UUID) -> Optional[DocumentResponse]:
        """Get document by ID"""
        
        document = await self.document_repo.get_document_by_id(document_id, user_id)
        if not document:
            return None
        
        return DocumentResponse.model_validate(document)
    
    async def list_documents(
        self,
        user_id: UUID,
        file_type: Optional[str] = None,
        processing_status: Optional[str] = None,
        search: Optional[str] = None,
        visibility: Optional[str] = None,
        pagination: Optional[PaginationParams] = None
    ) -> tuple[List[DocumentResponse], int]:
        """List documents with filtering"""
        
        documents, total = await self.document_repo.list_documents(
            user_id=user_id,
            file_type=file_type,
            processing_status=processing_status,
            search=search,
            visibility=visibility,
            pagination=pagination
        )
        
        document_responses = [DocumentResponse.model_validate(doc) for doc in documents]
        return document_responses, total
    
    async def search_documents(
        self,
        request: DocumentSearchRequest,
        user_id: UUID
    ) -> DocumentSearchResponse:
        """Search documents using various methods"""
        
        start_time = time.time()
        
        if request.search_type == "vector":
            results = await self._vector_search(request, user_id)
        elif request.search_type == "keyword":
            results = await self._keyword_search(request, user_id)
        else:  # hybrid
            results = await self._hybrid_search(request, user_id)
        
        search_time = time.time() - start_time
        
        return DocumentSearchResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            search_time=search_time,
            search_type=request.search_type
        )
    
    async def delete_document(self, document_id: UUID, user_id: UUID) -> bool:
        """Delete a document and its chunks"""
        
        # Delete from vector store first
        await self._delete_document_from_vector_store(document_id)
        
        # Delete from database
        return await self.document_repo.delete_document(document_id, user_id)
    
    async def share_document(
        self,
        document_id: UUID,
        user_id: UUID,
        shared_with: List[UUID]
    ) -> bool:
        """Share document with specified users"""
        
        return await self.document_repo.share_document(document_id, user_id, shared_with)
    
    async def get_document_chunks(
        self,
        document_id: UUID,
        user_id: UUID,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get chunks for a document"""
        
        # Verify document access
        document = await self.document_repo.get_document_by_id(document_id, user_id)
        if not document:
            return []
        
        chunks = await self.chunk_repo.get_document_chunks(document_id, limit)
        
        return [
            {
                'id': chunk.id,
                'chunk_index': chunk.chunk_index,
                'content': chunk.content,
                'metadata': chunk.chunk_metadata,
                'quality_score': chunk.quality_score,
                'token_count': chunk.token_count,
                'section_title': chunk.section_title,
                'page_number': chunk.page_number
            }
            for chunk in chunks
        ]
    
    async def get_processing_status(self) -> Dict[str, Any]:
        """Get document processing status overview"""
        
        pending_docs = await self.document_repo.get_documents_for_processing()
        
        return {
            'pending_documents': len(pending_docs),
            'processing_queue': [
                {
                    'id': doc.id,
                    'name': doc.name,
                    'file_type': doc.file_type,
                    'created_at': doc.created_at
                }
                for doc in pending_docs[:10]  # Show first 10
            ]
        }
    
    async def reprocess_document(self, document_id: UUID, user_id: UUID) -> bool:
        """Reprocess a document"""
        
        # Verify ownership
        document = await self.document_repo.get_document_by_id(document_id, user_id)
        if not document:
            return False
        
        # Reset processing status
        await self.document_repo.update_processing_status(document_id, "pending")
        
        # Process asynchronously
        asyncio.create_task(self._process_document_async(document_id))
        
        return True
    
    async def _process_document_async(self, document_id: UUID):
        """Process document asynchronously"""
        
        try:
            # Update status to processing
            await self.document_repo.update_processing_status(document_id, "processing")
            
            # Get document
            document = await self.document_repo.get_document_by_id(document_id)
            if not document:
                return
            
            # Get processor for file type
            processor = self.document_processors.get(document.file_type)
            if not processor:
                await self.document_repo.update_processing_status(
                    document_id, "failed"
                )
                return
            
            # Process document content
            processed_content = await processor.process(document.content, document.metadata)
            
            # Split into chunks
            chunks = await self._split_document_into_chunks(document, processed_content)
            
            # Generate embeddings for chunks
            embedded_chunks = await self._generate_chunk_embeddings(chunks)
            
            # Store chunks in database
            chunk_records = []
            for i, chunk in enumerate(embedded_chunks):
                chunk_data = {
                    'document_id': document_id,
                    'chunk_index': i,
                    'content': chunk['content'],
                    'chunk_metadata': chunk['metadata'],
                    'start_position': chunk.get('start_position', 0),
                    'end_position': chunk.get('end_position', 0),
                    'page_number': chunk.get('page_number'),
                    'section_title': chunk.get('section_title'),
                    'embedding_model': chunk['embedding_model'],
                    'embedding_dimension': len(chunk['embedding']),
                    'quality_score': chunk['quality_score'],
                    'token_count': chunk['token_count'],
                    'created_at': datetime.utcnow()
                }
                chunk_records.append(chunk_data)
            
            stored_chunks = await self.chunk_repo.create_chunks(chunk_records)
            
            # Store embeddings in vector store
            await self._store_chunks_in_vector_store(stored_chunks, embedded_chunks)
            
            # Calculate quality score
            avg_quality = sum(chunk['quality_score'] for chunk in embedded_chunks) / len(embedded_chunks)
            
            # Update document status
            await self.document_repo.update_processing_status(
                document_id,
                "completed",
                chunk_count=len(chunks),
                quality_score=avg_quality
            )
            
        except Exception as e:
            # Update status to failed
            await self.document_repo.update_processing_status(document_id, "failed")
            # Log error (in production, use proper logging)
            print(f"Document processing failed for {document_id}: {str(e)}")
    
    async def _split_document_into_chunks(
        self,
        document,
        processed_content: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Split document into chunks"""
        
        chunks = []
        content = processed_content['content']
        
        # Simple text splitting (in production, use more sophisticated methods)
        chunk_size = 512  # tokens
        overlap = 50     # tokens
        
        # Estimate token count (rough approximation)
        words = content.split()
        estimated_tokens = len(words) * 1.3  # Rough conversion
        
        if estimated_tokens <= chunk_size:
            # Single chunk
            chunks.append({
                'content': content,
                'metadata': processed_content.get('metadata', {}),
                'start_position': 0,
                'end_position': len(content),
                'quality_score': self._calculate_chunk_quality(content),
                'token_count': int(estimated_tokens)
            })
        else:
            # Multiple chunks
            sentences = content.split('. ')
            current_chunk = ""
            current_tokens = 0
            start_pos = 0
            
            for sentence in sentences:
                sentence_tokens = len(sentence.split()) * 1.3
                
                if current_tokens + sentence_tokens > chunk_size and current_chunk:
                    # Save current chunk
                    chunks.append({
                        'content': current_chunk.strip(),
                        'metadata': processed_content.get('metadata', {}),
                        'start_position': start_pos,
                        'end_position': start_pos + len(current_chunk),
                        'quality_score': self._calculate_chunk_quality(current_chunk),
                        'token_count': int(current_tokens)
                    })
                    
                    # Start new chunk with overlap
                    overlap_content = '. '.join(current_chunk.split('. ')[-2:]) if '. ' in current_chunk else ""
                    start_pos += len(current_chunk) - len(overlap_content)
                    current_chunk = overlap_content + ". " + sentence
                    current_tokens = len(overlap_content.split()) * 1.3 + sentence_tokens
                else:
                    current_chunk += ". " + sentence if current_chunk else sentence
                    current_tokens += sentence_tokens
            
            # Add final chunk
            if current_chunk:
                chunks.append({
                    'content': current_chunk.strip(),
                    'metadata': processed_content.get('metadata', {}),
                    'start_position': start_pos,
                    'end_position': start_pos + len(current_chunk),
                    'quality_score': self._calculate_chunk_quality(current_chunk),
                    'token_count': int(current_tokens)
                })
        
        return chunks
    
    async def _generate_chunk_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate embeddings for chunks"""
        
        embedded_chunks = []
        
        for chunk in chunks:
            # Generate embedding
            embedding = await self.embedding_service.embed_text(chunk['content'])
            
            embedded_chunk = {
                **chunk,
                'embedding': embedding,
                'embedding_model': self.embedding_service.model_name
            }
            embedded_chunks.append(embedded_chunk)
        
        return embedded_chunks
    
    async def _store_chunks_in_vector_store(self, stored_chunks, embedded_chunks):
        """Store chunk embeddings in vector store"""
        
        for stored_chunk, embedded_chunk in zip(stored_chunks, embedded_chunks):
            await self.vector_store.store(
                id=str(stored_chunk.id),
                vector=embedded_chunk['embedding'],
                metadata={
                    'document_id': str(stored_chunk.document_id),
                    'chunk_index': stored_chunk.chunk_index,
                    'content': stored_chunk.content,
                    'quality_score': stored_chunk.quality_score
                }
            )
    
    async def _vector_search(
        self,
        request: DocumentSearchRequest,
        user_id: UUID
    ) -> List[DocumentSearchResult]:
        """Perform vector similarity search"""
        
        # Generate query embedding
        query_embedding = await self.embedding_service.embed_text(request.query)
        
        # Search in vector store
        vector_results = await self.vector_store.search(
            query_vector=query_embedding,
            top_k=request.top_k,
            filters=request.filters
        )
        
        # Get chunk details from database
        chunk_ids = [UUID(result['id']) for result in vector_results]
        chunks = await self.chunk_repo.get_chunks_by_ids(chunk_ids)
        
        # Convert to search results
        results = []
        for chunk in chunks:
            # Find corresponding vector result for score
            vector_result = next((r for r in vector_results if r['id'] == str(chunk.id)), None)
            relevance_score = vector_result['score'] if vector_result else 0.0
            
            # Get document info
            document = await self.document_repo.get_document_by_id(chunk.document_id, user_id)
            if not document:
                continue
            
            result = DocumentSearchResult(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                content=chunk.content,
                metadata=chunk.chunk_metadata,
                relevance_score=relevance_score,
                document_name=document.name,
                section_title=chunk.section_title,
                page_number=chunk.page_number
            )
            results.append(result)
        
        return results
    
    async def _keyword_search(
        self,
        request: DocumentSearchRequest,
        user_id: UUID
    ) -> List[DocumentSearchResult]:
        """Perform keyword-based search"""
        
        # Get accessible document IDs for user
        documents, _ = await self.document_repo.list_documents(user_id=user_id)
        document_ids = [doc.id for doc in documents]
        
        if not document_ids:
            return []
        
        # Search chunks by text
        chunks = await self.chunk_repo.search_chunks_by_text(
            query=request.query,
            document_ids=document_ids,
            limit=request.top_k
        )
        
        results = []
        for chunk in chunks:
            document = await self.document_repo.get_document_by_id(chunk.document_id, user_id)
            if not document:
                continue
            
            # Calculate relevance score (simple keyword matching)
            relevance_score = self._calculate_keyword_relevance(request.query, chunk.content)
            
            result = DocumentSearchResult(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                content=chunk.content,
                metadata=chunk.chunk_metadata,
                relevance_score=relevance_score,
                document_name=document.name,
                section_title=chunk.section_title,
                page_number=chunk.page_number
            )
            results.append(result)
        
        # Sort by relevance
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return results
    
    async def _hybrid_search(
        self,
        request: DocumentSearchRequest,
        user_id: UUID
    ) -> List[DocumentSearchResult]:
        """Perform hybrid search combining vector and keyword search"""
        
        # Perform both searches
        vector_results = await self._vector_search(request, user_id)
        keyword_results = await self._keyword_search(request, user_id)
        
        # Combine and deduplicate results
        combined_results = {}
        
        # Add vector results with weight
        for result in vector_results:
            combined_results[result.chunk_id] = result
            combined_results[result.chunk_id].relevance_score *= 0.7  # Vector weight
        
        # Add keyword results with weight
        for result in keyword_results:
            if result.chunk_id in combined_results:
                # Combine scores
                combined_results[result.chunk_id].relevance_score += result.relevance_score * 0.3
            else:
                result.relevance_score *= 0.3  # Keyword weight
                combined_results[result.chunk_id] = result
        
        # Sort by combined score
        final_results = list(combined_results.values())
        final_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return final_results[:request.top_k]
    
    async def _delete_document_from_vector_store(self, document_id: UUID):
        """Delete document chunks from vector store"""
        
        chunks = await self.chunk_repo.get_document_chunks(document_id)
        chunk_ids = [str(chunk.id) for chunk in chunks]
        
        if chunk_ids:
            await self.vector_store.delete(chunk_ids)
    
    def _calculate_chunk_quality(self, content: str) -> float:
        """Calculate quality score for a chunk"""
        
        # Simple quality metrics
        score = 0.5  # Base score
        
        # Length score
        if 50 <= len(content) <= 1000:
            score += 0.2
        
        # Sentence completeness
        if content.strip().endswith(('.', '!', '?')):
            score += 0.1
        
        # Has meaningful content (not just punctuation/whitespace)
        if len(content.strip()) > 20 and any(c.isalnum() for c in content):
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_keyword_relevance(self, query: str, content: str) -> float:
        """Calculate keyword relevance score"""
        
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        if not query_words:
            return 0.0
        
        # Exact matches
        exact_matches = len(query_words.intersection(content_words))
        relevance = exact_matches / len(query_words)
        
        # Boost for phrase matches
        if query.lower() in content.lower():
            relevance += 0.3
        
        return min(relevance, 1.0)


# Document processor classes (simplified implementations)

class DocumentProcessor:
    """Base document processor"""
    
    async def process(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process document content"""
        return {
            'content': content,
            'metadata': metadata
        }


class PDFProcessor(DocumentProcessor):
    """PDF document processor"""
    
    async def process(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        # In production, use proper PDF parsing libraries
        return {
            'content': content,
            'metadata': {**metadata, 'processed_type': 'pdf'}
        }


class DocxProcessor(DocumentProcessor):
    """DOCX document processor"""
    
    async def process(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        # In production, use proper DOCX parsing libraries
        return {
            'content': content,
            'metadata': {**metadata, 'processed_type': 'docx'}
        }


class TextProcessor(DocumentProcessor):
    """Plain text processor"""
    
    async def process(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'content': content.strip(),
            'metadata': {**metadata, 'processed_type': 'text'}
        }


class MarkdownProcessor(DocumentProcessor):
    """Markdown processor"""
    
    async def process(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        # In production, parse markdown structure
        return {
            'content': content,
            'metadata': {**metadata, 'processed_type': 'markdown'}
        }


class HTMLProcessor(DocumentProcessor):
    """HTML processor"""
    
    async def process(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        # In production, extract text from HTML
        return {
            'content': content,
            'metadata': {**metadata, 'processed_type': 'html'}
        }


# Placeholder service classes

class EmbeddingService:
    """Embedding service for generating text embeddings"""
    
    def __init__(self):
        self.model_name = "text-embedding-3-small"
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text"""
        # In production, call actual embedding API
        # Return mock embedding for now
        return [0.1] * 1536  # OpenAI embedding dimension


class VectorStore:
    """Vector store for storing and searching embeddings"""
    
    async def store(self, id: str, vector: List[float], metadata: Dict[str, Any]):
        """Store vector in vector database"""
        # In production, store in actual vector database (pgvector, Chroma, etc.)
        pass
    
    async def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        # In production, perform actual vector search
        # Return mock results for now
        return [
            {'id': f'chunk_{i}', 'score': 0.9 - (i * 0.1)}
            for i in range(top_k)
        ]
    
    async def delete(self, ids: List[str]):
        """Delete vectors by IDs"""
        # In production, delete from actual vector database
        pass