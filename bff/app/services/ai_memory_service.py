"""AI Memory service for three-tier memory management system."""

import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID, uuid4

from app.infrastructure.database.repositories.ai_memory_repository_impl import (
    AIMemoryRepositoryImpl,
    AIConversationSummaryRepositoryImpl
)
from app.schemas.ai import (
    MemoryCreate,
    MemoryResponse,
    MemoryType,
    MemoryCategory,
    ConversationSummaryResponse
)
from app.services.base import BaseService


class AIMemoryService(BaseService):
    """AI Memory service for managing three-tier memory system"""
    
    def __init__(self, session):
        super().__init__(session)
        self.memory_repo = AIMemoryRepositoryImpl(session)
        self.summary_repo = AIConversationSummaryRepositoryImpl(session)
    
    async def create_memory(self, memory_data: MemoryCreate, user_id: UUID) -> MemoryResponse:
        """Create a new memory entry"""
        
        memory = await self.memory_repo.create_memory(memory_data, user_id)
        return MemoryResponse.model_validate(memory)
    
    async def store_short_term_memory(
        self,
        conversation_id: UUID,
        content: str,
        user_id: UUID,
        agent_id: Optional[UUID] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MemoryResponse:
        """Store short-term memory (working memory)"""
        
        memory_data = MemoryCreate(
            conversation_id=conversation_id,
            agent_id=agent_id,
            memory_type=MemoryType.SHORT_TERM,
            memory_category=MemoryCategory.CONVERSATION,
            content=content,
            metadata=metadata or {},
            importance_score=0.5,
            confidence_score=1.0
        )
        
        return await self.create_memory(memory_data, user_id)
    
    async def get_conversation_context(
        self,
        conversation_id: UUID,
        limit: int = 10
    ) -> List[MemoryResponse]:
        """Get recent context for a conversation"""
        
        memories = await self.memory_repo.get_memories_by_conversation(
            conversation_id=conversation_id,
            memory_type=MemoryType.SHORT_TERM,
            limit=limit
        )
        
        return [MemoryResponse.model_validate(memory) for memory in memories]
    
    async def get_user_memories(
        self,
        user_id: UUID,
        memory_type: Optional[MemoryType] = None,
        memory_category: Optional[MemoryCategory] = None,
        limit: int = 20
    ) -> List[MemoryResponse]:
        """Get memories for a user"""
        
        memories = await self.memory_repo.get_memories_by_user(
            user_id=user_id,
            memory_type=memory_type,
            memory_category=memory_category,
            limit=limit
        )
        
        return [MemoryResponse.model_validate(memory) for memory in memories]
    
    async def search_memories(
        self,
        user_id: UUID,
        query: str,
        memory_type: Optional[MemoryType] = None,
        conversation_id: Optional[UUID] = None,
        limit: int = 10
    ) -> List[MemoryResponse]:
        """Search memories by content"""
        
        memories = await self.memory_repo.search_memories(
            user_id=user_id,
            query=query,
            memory_type=memory_type,
            conversation_id=conversation_id,
            limit=limit
        )
        
        # Update access statistics
        for memory in memories:
            await self.memory_repo.update_memory_access(memory.id)
        
        return [MemoryResponse.model_validate(memory) for memory in memories]
    
    async def compress_short_to_medium_term(self, conversation_id: UUID) -> Optional[ConversationSummaryResponse]:
        """Compress short-term memories to medium-term summary"""
        
        # Get short-term memories for the conversation
        short_term_memories = await self.memory_repo.get_memories_by_conversation(
            conversation_id=conversation_id,
            memory_type=MemoryType.SHORT_TERM
        )
        
        if not short_term_memories:
            return None
        
        # Create conversation summary
        summary_data = await self._create_conversation_summary(conversation_id, short_term_memories)
        summary = await self.summary_repo.create_summary(summary_data)
        
        # Create medium-term memory entries from summary
        await self._create_medium_term_memories(summary, short_term_memories[0].user_id)
        
        # Clean up old short-term memories (keep recent ones)
        await self._cleanup_short_term_memories(conversation_id, keep_recent=5)
        
        return ConversationSummaryResponse.model_validate(summary)
    
    async def get_conversation_summaries(
        self,
        conversation_id: UUID,
        limit: Optional[int] = None
    ) -> List[ConversationSummaryResponse]:
        """Get summaries for a conversation"""
        
        summaries = await self.summary_repo.get_conversation_summaries(conversation_id, limit)
        return [ConversationSummaryResponse.model_validate(summary) for summary in summaries]
    
    async def search_conversation_summaries(
        self,
        query: str,
        conversation_id: Optional[UUID] = None,
        limit: int = 10
    ) -> List[ConversationSummaryResponse]:
        """Search conversation summaries"""
        
        summaries = await self.summary_repo.search_summaries(query, conversation_id, limit)
        return [ConversationSummaryResponse.model_validate(summary) for summary in summaries]
    
    async def get_contextual_memories(
        self,
        user_id: UUID,
        conversation_id: UUID,
        current_context: str,
        max_memories: int = 10
    ) -> List[MemoryResponse]:
        """Get contextually relevant memories for AI generation"""
        
        memories = []
        
        # 1. Get recent short-term memories
        recent_memories = await self.memory_repo.get_memories_by_conversation(
            conversation_id=conversation_id,
            memory_type=MemoryType.SHORT_TERM,
            limit=5
        )
        memories.extend(recent_memories)
        
        # 2. Get relevant medium-term memories
        if current_context:
            medium_term_memories = await self.memory_repo.search_memories(
                user_id=user_id,
                query=current_context,
                memory_type=MemoryType.MEDIUM_TERM,
                limit=3
            )
            memories.extend(medium_term_memories)
        
        # 3. Get important long-term memories
        long_term_memories = await self.memory_repo.get_memories_by_user(
            user_id=user_id,
            memory_type=MemoryType.LONG_TERM,
            limit=2
        )
        memories.extend(long_term_memories)
        
        # Sort by importance and recency, limit results
        sorted_memories = sorted(
            memories,
            key=lambda m: (m.importance_score, m.last_accessed_at),
            reverse=True
        )[:max_memories]
        
        # Update access statistics
        for memory in sorted_memories:
            await self.memory_repo.update_memory_access(memory.id)
        
        return [MemoryResponse.model_validate(memory) for memory in sorted_memories]
    
    async def extract_important_information(
        self,
        conversation_id: UUID,
        messages: List[Dict[str, Any]],
        user_id: UUID
    ) -> List[MemoryResponse]:
        """Extract important information from conversation messages"""
        
        important_memories = []
        
        # TODO: Integrate with LLM for intelligent extraction
        # For now, use simple heuristics
        for message in messages:
            content = message.get('content', '')
            
            # Check for important patterns
            importance_score = self._calculate_importance_score(content)
            if importance_score > 0.7:
                memory_data = MemoryCreate(
                    conversation_id=conversation_id,
                    agent_id=message.get('agent_id'),
                    memory_type=MemoryType.MEDIUM_TERM,
                    memory_category=self._categorize_content(content),
                    content=content,
                    metadata={
                        'extracted_from': 'conversation',
                        'message_id': message.get('id'),
                        'extraction_method': 'heuristic'
                    },
                    importance_score=importance_score,
                    confidence_score=0.8
                )
                
                memory = await self.create_memory(memory_data, user_id)
                important_memories.append(memory)
        
        return important_memories
    
    async def cleanup_expired_memories(self) -> int:
        """Clean up expired memories"""
        
        return await self.memory_repo.delete_expired_memories()
    
    async def get_memory_statistics(self, user_id: UUID) -> Dict[str, Any]:
        """Get memory usage statistics for a user"""
        
        return await self.memory_repo.get_memory_statistics(user_id)
    
    async def _create_conversation_summary(
        self,
        conversation_id: UUID,
        memories: List
    ) -> Dict[str, Any]:
        """Create conversation summary from memories"""
        
        # Extract content from memories
        all_content = [memory.content for memory in memories]
        combined_content = " ".join(all_content)
        
        # TODO: Use LLM for intelligent summarization
        # For now, use simple extraction
        key_points = await self._extract_key_points(combined_content)
        entities = await self._extract_entities(combined_content)
        topics = await self._extract_topics(combined_content)
        sentiment = await self._analyze_sentiment(combined_content)
        
        return {
            'conversation_id': conversation_id,
            'agent_id': memories[0].agent_id if memories else None,
            'summary_text': self._create_summary_text(combined_content),
            'key_points': key_points,
            'entities': entities,
            'topics': topics,
            'sentiment': sentiment,
            'time_range_start': min(memory.created_at for memory in memories),
            'time_range_end': max(memory.created_at for memory in memories),
            'message_count': len(memories),
            'participant_count': len(set(memory.user_id for memory in memories if memory.user_id)),
            'summary_quality_score': 0.8,  # TODO: Calculate actual quality score
            'completeness_score': 0.85,
            'created_at': datetime.utcnow()
        }
    
    async def _create_medium_term_memories(self, summary, user_id: UUID):
        """Create medium-term memories from conversation summary"""
        
        # Create memories for key points
        for key_point in summary.key_points:
            memory_data = MemoryCreate(
                conversation_id=summary.conversation_id,
                agent_id=summary.agent_id,
                memory_type=MemoryType.MEDIUM_TERM,
                memory_category=MemoryCategory.CONVERSATION,
                content=key_point,
                metadata={
                    'source': 'summary',
                    'summary_id': str(summary.id)
                },
                importance_score=0.8,
                confidence_score=summary.summary_quality_score
            )
            
            await self.create_memory(memory_data, user_id)
        
        # Create memories for entities
        for entity in summary.entities:
            if isinstance(entity, dict) and 'text' in entity:
                memory_data = MemoryCreate(
                    conversation_id=summary.conversation_id,
                    agent_id=summary.agent_id,
                    memory_type=MemoryType.MEDIUM_TERM,
                    memory_category=MemoryCategory.ENTITY,
                    content=entity['text'],
                    metadata={
                        'source': 'summary',
                        'entity_type': entity.get('type', 'unknown'),
                        'summary_id': str(summary.id)
                    },
                    importance_score=0.7,
                    confidence_score=entity.get('confidence', 0.8)
                )
                
                await self.create_memory(memory_data, user_id)
    
    async def _cleanup_short_term_memories(self, conversation_id: UUID, keep_recent: int = 5):
        """Clean up old short-term memories, keeping recent ones"""
        
        memories = await self.memory_repo.get_memories_by_conversation(
            conversation_id=conversation_id,
            memory_type=MemoryType.SHORT_TERM
        )
        
        if len(memories) > keep_recent:
            # Sort by creation time and keep only recent ones
            memories.sort(key=lambda m: m.created_at, reverse=True)
            to_delete = memories[keep_recent:]
            
            # Delete old memories
            for memory in to_delete:
                await self.session.delete(memory)
            
            await self.session.commit()
    
    def _calculate_importance_score(self, content: str) -> float:
        """Calculate importance score for content"""
        
        important_keywords = [
            'important', 'remember', 'note', 'todo', 'action', 'decision',
            'deadline', 'meeting', 'appointment', 'contact', 'phone', 'email'
        ]
        
        content_lower = content.lower()
        score = 0.5  # Base score
        
        for keyword in important_keywords:
            if keyword in content_lower:
                score += 0.1
        
        # Boost score for questions and action items
        if '?' in content:
            score += 0.1
        if any(word in content_lower for word in ['need to', 'should', 'must', 'have to']):
            score += 0.15
        
        return min(score, 1.0)
    
    def _categorize_content(self, content: str) -> MemoryCategory:
        """Categorize content into memory categories"""
        
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['like', 'prefer', 'favorite', 'hate', 'dislike']):
            return MemoryCategory.USER_PREFERENCE
        elif any(word in content_lower for word in ['person', 'people', 'contact', 'friend', 'colleague']):
            return MemoryCategory.ENTITY
        elif any(word in content_lower for word in ['learn', 'know', 'understand', 'information', 'fact']):
            return MemoryCategory.KNOWLEDGE
        elif any(word in content_lower for word in ['always', 'usually', 'often', 'typically', 'pattern']):
            return MemoryCategory.PATTERN
        else:
            return MemoryCategory.CONVERSATION
    
    async def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from content (simplified version)"""
        
        # Split content into sentences and return important ones
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        
        key_sentences = []
        for sentence in sentences[:10]:  # Limit to avoid too many points
            if len(sentence) > 20 and self._calculate_importance_score(sentence) > 0.6:
                key_sentences.append(sentence)
        
        return key_sentences[:5]  # Return top 5 key points
    
    async def _extract_entities(self, content: str) -> List[Dict[str, Any]]:
        """Extract entities from content (simplified version)"""
        
        # TODO: Use NER model for proper entity extraction
        # For now, use simple patterns
        
        import re
        
        entities = []
        
        # Extract email addresses
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
        for email in emails:
            entities.append({'text': email, 'type': 'email', 'confidence': 0.9})
        
        # Extract phone numbers (simple pattern)
        phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', content)
        for phone in phones:
            entities.append({'text': phone, 'type': 'phone', 'confidence': 0.8})
        
        # Extract dates (simple patterns)
        dates = re.findall(r'\b\d{1,2}/\d{1,2}/\d{4}\b|\b\d{4}-\d{2}-\d{2}\b', content)
        for date in dates:
            entities.append({'text': date, 'type': 'date', 'confidence': 0.7})
        
        return entities
    
    async def _extract_topics(self, content: str) -> List[str]:
        """Extract topics from content (simplified version)"""
        
        # TODO: Use topic modeling for proper topic extraction
        # For now, use keyword frequency
        
        import re
        from collections import Counter
        
        # Clean and tokenize content
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        
        # Common stop words to exclude
        stop_words = set([
            'that', 'this', 'with', 'have', 'will', 'from', 'they', 'been',
            'have', 'were', 'said', 'each', 'which', 'their', 'time', 'will'
        ])
        
        # Filter words and count frequency
        filtered_words = [word for word in words if word not in stop_words]
        word_counts = Counter(filtered_words)
        
        # Return top topics
        return [word for word, count in word_counts.most_common(5) if count > 1]
    
    async def _analyze_sentiment(self, content: str) -> str:
        """Analyze sentiment of content (simplified version)"""
        
        # TODO: Use sentiment analysis model
        # For now, use simple keyword-based approach
        
        positive_words = ['good', 'great', 'excellent', 'happy', 'love', 'like', 'wonderful']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'horrible', 'sad']
        
        content_lower = content.lower()
        
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _create_summary_text(self, content: str) -> str:
        """Create summary text from content (simplified version)"""
        
        # TODO: Use abstractive summarization model
        # For now, return first few sentences with key information
        
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        
        if len(sentences) <= 3:
            return content
        
        # Return first sentence and most important ones
        summary_sentences = [sentences[0]]
        
        for sentence in sentences[1:]:
            if self._calculate_importance_score(sentence) > 0.7 and len(summary_sentences) < 3:
                summary_sentences.append(sentence)
        
        return '. '.join(summary_sentences) + '.'