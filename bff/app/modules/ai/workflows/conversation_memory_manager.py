"""
Conversation Memory Manager (Priority 5)
Enhanced memory management system that integrates with LangGraph workflows.
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.memory.service import AIMemoryService
from app.modules.ai.memory.schemas import MemoryCategory, MemoryType
from app.modules.ai.workflows.state_models import ContactInfo, ConversationState
from app.core.services import BaseService


class ConversationMemoryManager(BaseService):
    """Enhanced memory manager for LangGraph workflow integration."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.memory_service = AIMemoryService(session)
        
        # Memory configuration
        self.short_term_ttl_hours = 24  # Short term memory TTL
        self.medium_term_ttl_days = 30  # Medium term memory TTL
        self.max_context_memories = 10  # Max memories to include in context
        self.similarity_threshold = 0.7  # Similarity threshold for memory retrieval
        
    async def get_conversation_context(
        self,
        conversation_id: UUID,
        user_id: UUID,
        current_message: str,
        max_memories: int = None
    ) -> Dict[str, Any]:
        """Get enhanced conversation context including relevant memories."""
        
        max_memories = max_memories or self.max_context_memories
        
        # Get recent short-term memories
        short_term_memories = await self.memory_service.get_contextual_memories(
            user_id=user_id,
            conversation_id=conversation_id,
            current_context=current_message,
            max_memories=max_memories // 2
        )
        
        # Get relevant medium/long-term memories based on content similarity
        relevant_memories = await self._get_relevant_memories(
            user_id=user_id,
            current_context=current_message,
            conversation_id=conversation_id,
            max_memories=max_memories // 2
        )
        
        # Get conversation summary if available
        conversation_summary = await self._get_conversation_summary(conversation_id)
        
        context = {
            "conversation_id": str(conversation_id),
            "short_term_memories": [
                {
                    "content": mem.content,
                    "importance": mem.importance_score,
                    "timestamp": mem.created_at.isoformat(),
                    "type": "short_term"
                } for mem in short_term_memories
            ],
            "relevant_memories": [
                {
                    "content": mem.content,
                    "importance": mem.importance_score,
                    "memory_type": mem.memory_type,
                    "timestamp": mem.created_at.isoformat(),
                    "relevance_score": getattr(mem, 'relevance_score', 0.8)
                } for mem in relevant_memories
            ],
            "conversation_summary": conversation_summary,
            "context_strength": self._calculate_context_strength(
                short_term_memories, relevant_memories
            )
        }
        
        return context

    async def store_workflow_memory(
        self,
        conversation_id: UUID,
        user_id: UUID,
        workflow_state: ConversationState,
        contact_responses: Dict[str, Any]
    ) -> List[str]:
        """Store memories from workflow execution."""
        
        stored_memory_ids = []
        
        # Store user message
        user_message_id = await self._store_user_message(
            conversation_id, user_id, workflow_state
        )
        if user_message_id:
            stored_memory_ids.append(user_message_id)
        
        # Store contact responses as memories
        for contact_id, response in contact_responses.items():
            if response.get("status") == "success" and response.get("response"):
                memory_id = await self._store_contact_response_memory(
                    conversation_id, user_id, contact_id, response, workflow_state
                )
                if memory_id:
                    stored_memory_ids.append(memory_id)
        
        # Store workflow metadata as memory
        if workflow_state.get("workflow_type") in ["debate_mode", "expert_panel", "comparison_routing"]:
            workflow_memory_id = await self._store_workflow_metadata_memory(
                conversation_id, user_id, workflow_state
            )
            if workflow_memory_id:
                stored_memory_ids.append(workflow_memory_id)
        
        return stored_memory_ids

    async def enhance_contact_context(
        self,
        contact: ContactInfo,
        user_id: UUID,
        current_message: str,
        conversation_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Enhance contact context with personalized memories."""
        
        # Get memories specific to this contact/agent
        contact_memories = await self._get_contact_specific_memories(
            user_id=user_id,
            agent_id=UUID(contact["agent_id"]),
            current_context=current_message,
            max_memories=5
        )
        
        # Get user's preferences and patterns with this contact
        interaction_patterns = await self._analyze_interaction_patterns(
            user_id, UUID(contact["agent_id"])
        )
        
        enhanced_context = {
            "contact_id": contact["contact_id"],
            "agent_id": contact["agent_id"],
            "display_name": contact["display_name"],
            "personal_memories": [
                {
                    "content": mem.content,
                    "importance": mem.importance_score,
                    "timestamp": mem.created_at.isoformat()
                } for mem in contact_memories
            ],
            "interaction_patterns": interaction_patterns,
            "memory_context_strength": len(contact_memories) / 5.0  # Normalized strength
        }
        
        return enhanced_context

    async def trigger_memory_consolidation(
        self,
        conversation_id: UUID,
        force_consolidation: bool = False
    ) -> Optional[str]:
        """Trigger memory consolidation process."""
        
        # Check if consolidation is needed
        if not force_consolidation:
            needs_consolidation = await self._check_consolidation_needed(conversation_id)
            if not needs_consolidation:
                return None
        
        # Perform consolidation
        try:
            summary = await self.memory_service.compress_short_to_medium_term(conversation_id)
            if summary:
                self.logger.info(f"Memory consolidation completed for conversation {conversation_id}")
                return summary.summary
            return None
        except Exception as e:
            self.logger.error(f"Memory consolidation failed: {e}")
            return None

    async def get_memory_insights(
        self,
        user_id: UUID,
        conversation_id: Optional[UUID] = None,
        agent_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Get memory insights and statistics."""
        
        # Get memory statistics
        stats = await self.memory_service.get_memory_statistics(user_id)
        
        # Calculate memory health metrics
        memory_health = await self._calculate_memory_health(user_id, conversation_id)
        
        # Get recent memory trends
        memory_trends = await self._analyze_memory_trends(user_id, agent_id)
        
        insights = {
            "statistics": stats,
            "memory_health": memory_health,
            "trends": memory_trends,
            "recommendations": await self._generate_memory_recommendations(
                stats, memory_health, memory_trends
            )
        }
        
        return insights

    # Private helper methods
    
    async def _get_relevant_memories(
        self,
        user_id: UUID,
        current_context: str,
        conversation_id: UUID,
        max_memories: int
    ) -> List[Any]:
        """Get relevant memories using semantic similarity."""
        
        # For now, use keyword-based matching
        # In production, this would use vector similarity search
        memories = await self.memory_service.search_memories(
            user_id=user_id,
            query=current_context,
            memory_type=None,  # All types
            conversation_id=None,  # Cross-conversation search
            limit=max_memories
        )
        
        # Filter out memories from current conversation (to avoid duplication)
        return [mem for mem in memories 
                if mem.conversation_id != conversation_id]
    
    async def _get_conversation_summary(self, conversation_id: UUID) -> Optional[Dict[str, Any]]:
        """Get conversation summary if available."""
        
        try:
            summaries = await self.memory_service.get_conversation_summaries(
                conversation_id, limit=1
            )
            if summaries:
                summary = summaries[0]
                return {
                    "summary": summary.summary,
                    "key_topics": summary.key_topics,
                    "created_at": summary.created_at.isoformat(),
                    "importance": summary.importance_score
                }
        except Exception as e:
            self.logger.warning(f"Failed to get conversation summary: {e}")
        
        return None
    
    def _calculate_context_strength(self, short_term_memories: List, relevant_memories: List) -> float:
        """Calculate the strength of available context."""
        
        if not short_term_memories and not relevant_memories:
            return 0.0
        
        # Weight recent memories higher
        short_term_weight = len(short_term_memories) * 0.7
        relevant_weight = len(relevant_memories) * 0.3
        
        total_strength = (short_term_weight + relevant_weight) / self.max_context_memories
        return min(total_strength, 1.0)
    
    async def _store_user_message(
        self,
        conversation_id: UUID,
        user_id: UUID,
        workflow_state: ConversationState
    ) -> Optional[str]:
        """Store user message as memory."""
        
        try:
            memory = await self.memory_service.store_short_term_memory(
                conversation_id=conversation_id,
                content=workflow_state["current_message"],
                user_id=user_id,
                metadata={
                    "message_type": "user_input",
                    "workflow_execution_id": workflow_state.get("workflow_execution_id"),
                    "timestamp": workflow_state.get("started_at")
                }
            )
            return str(memory.id)
        except Exception as e:
            self.logger.error(f"Failed to store user message memory: {e}")
            return None
    
    async def _store_contact_response_memory(
        self,
        conversation_id: UUID,
        user_id: UUID,
        contact_id: str,
        response: Dict[str, Any],
        workflow_state: ConversationState
    ) -> Optional[str]:
        """Store contact response as memory."""
        
        try:
            # Calculate importance based on response quality and workflow context
            importance_score = self._calculate_response_importance(response, workflow_state)
            
            memory = await self.memory_service.store_short_term_memory(
                conversation_id=conversation_id,
                content=response["response"],
                user_id=user_id,
                agent_id=UUID(response.get("agent_id")) if response.get("agent_id") else None,
                metadata={
                    "message_type": "contact_response",
                    "contact_id": contact_id,
                    "contact_name": response.get("contact_name"),
                    "workflow_type": workflow_state.get("workflow_type"),
                    "tokens_used": response.get("tokens_used"),
                    "model_used": response.get("model_used"),
                    "importance_score": importance_score
                }
            )
            return str(memory.id)
        except Exception as e:
            self.logger.error(f"Failed to store contact response memory: {e}")
            return None
    
    async def _store_workflow_metadata_memory(
        self,
        conversation_id: UUID,
        user_id: UUID,
        workflow_state: ConversationState
    ) -> Optional[str]:
        """Store workflow metadata as structured memory."""
        
        try:
            # Create summary of workflow execution
            workflow_summary = {
                "workflow_type": workflow_state.get("workflow_type"),
                "routing_strategy": workflow_state.get("routing_strategy"),
                "participants": [c["display_name"] for c in workflow_state.get("active_contacts", [])],
                "execution_path": workflow_state.get("execution_path", []),
                "successful_responses": len([
                    r for r in workflow_state.get("contact_responses", {}).values()
                    if r.get("status") == "success"
                ])
            }
            
            memory = await self.memory_service.store_short_term_memory(
                conversation_id=conversation_id,
                content=f"Collaborative workflow executed: {workflow_summary['workflow_type']} with {', '.join(workflow_summary['participants'])}",
                user_id=user_id,
                metadata={
                    "message_type": "workflow_metadata",
                    "workflow_summary": workflow_summary,
                    "importance_score": 0.6  # Medium importance
                }
            )
            return str(memory.id)
        except Exception as e:
            self.logger.error(f"Failed to store workflow metadata memory: {e}")
            return None
    
    def _calculate_response_importance(
        self,
        response: Dict[str, Any],
        workflow_state: ConversationState
    ) -> float:
        """Calculate importance score for a response."""
        
        base_importance = 0.5
        
        # Increase importance for successful responses
        if response.get("status") == "success":
            base_importance += 0.2
        
        # Increase importance for longer, more detailed responses
        content_length = len(response.get("response", ""))
        if content_length > 200:
            base_importance += 0.1
        if content_length > 500:
            base_importance += 0.1
        
        # Increase importance for collaborative workflows
        workflow_type = workflow_state.get("workflow_type")
        if workflow_type in ["debate_mode", "expert_panel", "comparison_routing"]:
            base_importance += 0.2
        
        return min(base_importance, 1.0)
    
    async def _get_contact_specific_memories(
        self,
        user_id: UUID,
        agent_id: UUID,
        current_context: str,
        max_memories: int
    ) -> List[Any]:
        """Get memories specific to interactions with a particular contact/agent."""
        
        # Search memories where this agent was involved
        memories = await self.memory_service.search_memories(
            user_id=user_id,
            query=current_context,
            limit=max_memories * 2  # Get more to filter
        )
        
        # Filter to memories involving this specific agent
        agent_memories = []
        for memory in memories:
            if (memory.agent_id == agent_id or 
                (memory.metadata and memory.metadata.get("agent_id") == str(agent_id))):
                agent_memories.append(memory)
                if len(agent_memories) >= max_memories:
                    break
        
        return agent_memories
    
    async def _analyze_interaction_patterns(
        self,
        user_id: UUID,
        agent_id: UUID
    ) -> Dict[str, Any]:
        """Analyze interaction patterns between user and specific agent."""
        
        # This would involve more complex analysis in production
        patterns = {
            "preferred_communication_style": "detailed",  # Mock data
            "common_topics": ["programming", "web development"],
            "avg_session_length": "15 minutes",
            "interaction_frequency": "daily",
            "satisfaction_indicators": {
                "positive_feedback": 0.85,
                "task_completion_rate": 0.92
            }
        }
        
        return patterns
    
    async def _check_consolidation_needed(self, conversation_id: UUID) -> bool:
        """Check if memory consolidation is needed for the conversation."""
        
        # Get short-term memory count for this conversation
        try:
            # This would check the actual count in production
            # For now, trigger consolidation based on simple heuristics
            return True  # Always suggest consolidation for demo
        except Exception:
            return False
    
    async def _calculate_memory_health(
        self,
        user_id: UUID,
        conversation_id: Optional[UUID]
    ) -> Dict[str, Any]:
        """Calculate memory system health metrics."""
        
        return {
            "memory_freshness": 0.85,  # Mock data
            "consolidation_rate": 0.92,
            "retrieval_accuracy": 0.78,
            "storage_efficiency": 0.88,
            "context_relevance": 0.81
        }
    
    async def _analyze_memory_trends(
        self,
        user_id: UUID,
        agent_id: Optional[UUID]
    ) -> Dict[str, Any]:
        """Analyze memory usage and pattern trends."""
        
        return {
            "daily_memory_creation": [12, 15, 8, 20, 18, 14, 16],  # Last 7 days
            "top_categories": [
                {"category": "programming", "count": 45},
                {"category": "web_development", "count": 32},
                {"category": "general_discussion", "count": 28}
            ],
            "memory_retention_rate": 0.89,
            "cross_conversation_references": 15
        }
    
    async def _generate_memory_recommendations(
        self,
        stats: Dict[str, Any],
        health: Dict[str, Any],
        trends: Dict[str, Any]
    ) -> List[str]:
        """Generate memory system recommendations."""
        
        recommendations = []
        
        if health.get("consolidation_rate", 0) < 0.8:
            recommendations.append("Consider increasing memory consolidation frequency")
        
        if health.get("retrieval_accuracy", 0) < 0.75:
            recommendations.append("Memory retrieval accuracy could be improved with better categorization")
        
        if trends.get("memory_retention_rate", 0) < 0.85:
            recommendations.append("Review memory importance scoring to improve retention")
        
        if not recommendations:
            recommendations.append("Memory system is performing well")
        
        return recommendations
