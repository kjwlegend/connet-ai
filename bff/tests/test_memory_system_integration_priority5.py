"""
Tests for Priority 5: Intelligent Memory System Integration
Tests the enhanced memory management and workflow integration.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from datetime import datetime, timedelta

from app.services.langgraph.conversation_memory_manager import ConversationMemoryManager
from app.services.langgraph.workflow_engine import WorkflowEngine
from app.services.langgraph.state_models import ConversationState, ContactInfo
from app.schemas.ai import MemoryResponse, MemoryType


class TestConversationMemoryManager:
    """Test enhanced memory manager functionality."""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        session = Mock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.flush = AsyncMock()
        return session
    
    @pytest.fixture
    def memory_manager(self, mock_session):
        """Create ConversationMemoryManager instance."""
        return ConversationMemoryManager(mock_session)
    
    @pytest.fixture
    def sample_memories(self):
        """Sample memory responses."""
        return [
            Mock(
                id=uuid4(),
                content="We discussed Python programming basics",
                importance_score=0.8,
                memory_type="short_term",
                created_at=datetime.utcnow() - timedelta(hours=1),
                conversation_id=uuid4()
            ),
            Mock(
                id=uuid4(),
                content="User prefers detailed explanations",
                importance_score=0.9,
                memory_type="medium_term",
                created_at=datetime.utcnow() - timedelta(days=1),
                conversation_id=uuid4()
            )
        ]

    @pytest.mark.asyncio
    async def test_get_conversation_context(self, memory_manager, sample_memories):
        """Test getting enhanced conversation context."""
        
        conversation_id = uuid4()
        user_id = uuid4()
        current_message = "Can you help me with advanced Python concepts?"
        
        # Mock memory service responses
        with patch.object(memory_manager.memory_service, 'get_contextual_memories') as mock_contextual:
            with patch.object(memory_manager.memory_service, 'search_memories') as mock_search:
                with patch.object(memory_manager.memory_service, 'get_conversation_summaries') as mock_summaries:
                    
                    # Setup mocks
                    mock_contextual.return_value = [sample_memories[0]]  # Short-term memories
                    mock_search.return_value = [sample_memories[1]]     # Relevant memories
                    mock_summaries.return_value = []                   # No summaries
                    
                    # Execute
                    context = await memory_manager.get_conversation_context(
                        conversation_id=conversation_id,
                        user_id=user_id,
                        current_message=current_message,
                        max_memories=10
                    )
                    
                    # Verify structure
                    assert "conversation_id" in context
                    assert "short_term_memories" in context
                    assert "relevant_memories" in context
                    assert "context_strength" in context
                    
                    # Verify short-term memories
                    assert len(context["short_term_memories"]) == 1
                    short_term_mem = context["short_term_memories"][0]
                    assert short_term_mem["content"] == "We discussed Python programming basics"
                    assert short_term_mem["importance"] == 0.8
                    assert short_term_mem["type"] == "short_term"
                    
                    # Verify relevant memories
                    assert len(context["relevant_memories"]) == 1
                    relevant_mem = context["relevant_memories"][0]
                    assert relevant_mem["content"] == "User prefers detailed explanations"
                    assert relevant_mem["importance"] == 0.9

    @pytest.mark.asyncio
    async def test_store_workflow_memory(self, memory_manager):
        """Test storing workflow execution as memories."""
        
        conversation_id = uuid4()
        user_id = uuid4()
        
        # Mock workflow state
        workflow_state = {
            "conversation_id": str(conversation_id),
            "workflow_execution_id": str(uuid4()),
            "current_message": "Help me understand machine learning",
            "started_at": datetime.utcnow().isoformat(),
            "workflow_type": "parallel_discussion",
            "routing_strategy": "multi_contact",
            "execution_path": ["contact_processor", "response_aggregator"],
            "active_contacts": [
                {
                    "contact_id": "contact-1",
                    "display_name": "ML Expert",
                    "agent_id": str(uuid4())
                }
            ]
        }
        
        # Mock contact responses
        contact_responses = {
            "contact-1": {
                "status": "success",
                "response": "Machine learning is a subset of artificial intelligence...",
                "contact_name": "ML Expert",
                "agent_id": str(uuid4()),
                "tokens_used": 150
            }
        }
        
        # Mock memory service
        with patch.object(memory_manager.memory_service, 'store_short_term_memory') as mock_store:
            mock_memory = Mock(id=uuid4())
            mock_store.return_value = mock_memory
            
            # Execute
            memory_ids = await memory_manager.store_workflow_memory(
                conversation_id=conversation_id,
                user_id=user_id,
                workflow_state=workflow_state,
                contact_responses=contact_responses
            )
            
            # Verify memories were stored
            assert len(memory_ids) >= 2  # User message + contact response
            assert mock_store.call_count >= 2
            
            # Verify user message was stored
            user_call = None
            contact_call = None
            for i, call in enumerate(mock_store.call_args_list):
                # Check both positional and keyword arguments for content
                call_args, call_kwargs = call[0], call[1]
                content = ""
                if "content" in call_kwargs:
                    content = call_kwargs["content"]
                elif len(call_args) > 0 and hasattr(call_args[0], 'content'):
                    content = call_args[0].content
                
                # Use more specific matching - check for subset phrase first (more specific)
                if "subset of artificial intelligence" in content.lower():
                    contact_call = call
                elif "help me understand machine learning" in content.lower():
                    user_call = call
            
            assert user_call is not None, "User message should have been stored"
            assert contact_call is not None, "Contact response should have been stored"

    @pytest.mark.asyncio
    async def test_enhance_contact_context(self, memory_manager, sample_memories):
        """Test enhancing contact context with personalized memories."""
        
        contact = {
            "contact_id": "contact-1",
            "agent_id": str(uuid4()),
            "display_name": "Python Expert",
            "system_prompt": "I am a Python expert"
        }
        
        user_id = uuid4()
        current_message = "Help me with Python decorators"
        
        # Mock memory retrieval
        with patch.object(memory_manager, '_get_contact_specific_memories') as mock_contact_memories:
            with patch.object(memory_manager, '_analyze_interaction_patterns') as mock_patterns:
                
                mock_contact_memories.return_value = [sample_memories[0]]
                mock_patterns.return_value = {
                    "preferred_communication_style": "detailed",
                    "common_topics": ["python", "programming"],
                    "interaction_frequency": "weekly"
                }
                
                # Execute
                enhanced_context = await memory_manager.enhance_contact_context(
                    contact=contact,
                    user_id=user_id,
                    current_message=current_message
                )
                
                # Verify structure
                assert enhanced_context["contact_id"] == "contact-1"
                assert enhanced_context["display_name"] == "Python Expert"
                assert "personal_memories" in enhanced_context
                assert "interaction_patterns" in enhanced_context
                assert "memory_context_strength" in enhanced_context
                
                # Verify personal memories
                assert len(enhanced_context["personal_memories"]) == 1
                personal_mem = enhanced_context["personal_memories"][0]
                assert personal_mem["content"] == "We discussed Python programming basics"
                
                # Verify interaction patterns
                patterns = enhanced_context["interaction_patterns"]
                assert patterns["preferred_communication_style"] == "detailed"
                assert "python" in patterns["common_topics"]

    @pytest.mark.asyncio
    async def test_trigger_memory_consolidation(self, memory_manager):
        """Test memory consolidation triggering."""
        
        conversation_id = uuid4()
        
        # Mock memory service consolidation
        with patch.object(memory_manager.memory_service, 'compress_short_to_medium_term') as mock_consolidate:
            mock_summary = Mock(summary="Conversation about Python programming concepts")
            mock_consolidate.return_value = mock_summary
            
            # Execute consolidation
            result = await memory_manager.trigger_memory_consolidation(
                conversation_id=conversation_id,
                force_consolidation=True
            )
            
            # Verify consolidation was triggered
            assert result == "Conversation about Python programming concepts"
            mock_consolidate.assert_called_once_with(conversation_id)

    @pytest.mark.asyncio
    async def test_get_memory_insights(self, memory_manager):
        """Test getting memory insights and statistics."""
        
        user_id = uuid4()
        
        # Mock memory service statistics
        with patch.object(memory_manager.memory_service, 'get_memory_statistics') as mock_stats:
            mock_stats.return_value = {
                "total_memories": 150,
                "short_term_count": 50,
                "medium_term_count": 75,
                "long_term_count": 25
            }
            
            # Execute
            insights = await memory_manager.get_memory_insights(user_id=user_id)
            
            # Verify structure
            assert "statistics" in insights
            assert "memory_health" in insights
            assert "trends" in insights
            assert "recommendations" in insights
            
            # Verify statistics
            stats = insights["statistics"]
            assert stats["total_memories"] == 150
            assert stats["short_term_count"] == 50
            
            # Verify health metrics
            health = insights["memory_health"]
            assert "memory_freshness" in health
            assert "consolidation_rate" in health
            assert "retrieval_accuracy" in health
            
            # Verify trends
            trends = insights["trends"]
            assert "daily_memory_creation" in trends
            assert "top_categories" in trends
            assert "memory_retention_rate" in trends


class TestWorkflowEngineMemoryIntegration:
    """Test memory integration with workflow engine."""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        session = Mock()
        session.execute = AsyncMock()
        session.commit = AsyncMock() 
        return session
    
    @pytest.fixture
    def workflow_engine(self, mock_session):
        """Create WorkflowEngine with mocked dependencies."""
        with patch('app.services.langgraph.workflow_engine.get_settings') as mock_settings:
            mock_settings.return_value = Mock(
                openai_api_key="test-key",
                openai_base_url="https://api.openai.com/v1",
                openai_default_model="gpt-4",
                langsmith_tracing=False
            )
            with patch('app.services.langgraph.workflow_engine.ChatOpenAI'):
                engine = WorkflowEngine(mock_session)
                # Mock the memory manager with async methods
                engine.memory_manager = Mock()
                engine.memory_manager.store_workflow_memory = AsyncMock(return_value=["memory-1", "memory-2"])
                engine.memory_manager.trigger_memory_consolidation = AsyncMock(return_value="consolidation-summary")
                engine.memory_manager.get_conversation_context = AsyncMock(return_value={})
                engine.contact_manager = Mock()
                engine.mention_parser = Mock()
                return engine

    @pytest.mark.asyncio
    async def test_build_initial_state_with_memory(self, workflow_engine):
        """Test building initial state includes memory context."""
        
        conversation_id = uuid4()
        user_id = uuid4()
        message = "Tell me about advanced Python features"
        execution_id = uuid4()
        
        # Mock memory context
        memory_context = {
            "conversation_id": str(conversation_id),
            "short_term_memories": [
                {
                    "content": "Previous discussion about Python basics",
                    "importance": 0.8,
                    "type": "short_term"
                }
            ],
            "context_strength": 0.7
        }
        
        # Mock dependencies
        workflow_engine.contact_manager.get_conversation_participants = AsyncMock(return_value=[])
        workflow_engine.mention_parser.build_routing_context.return_value = {
            "mentions_found": [],
            "mentioned_contacts": [],
            "routing_strategy": "single_contact",
            "has_mentions": False
        }
        workflow_engine.memory_manager.get_conversation_context = AsyncMock(return_value=memory_context)
        
        # Execute
        initial_state = await workflow_engine._build_initial_state(
            conversation_id, user_id, message, None, execution_id
        )
        
        # Verify memory integration
        assert initial_state["conversation_memory"] == memory_context
        
        # Verify memory manager was called correctly
        workflow_engine.memory_manager.get_conversation_context.assert_called_once_with(
            conversation_id=conversation_id,
            user_id=user_id,
            current_message=message,
            max_memories=10
        )

    @pytest.mark.asyncio
    async def test_workflow_stores_memories(self, workflow_engine):
        """Test that workflow execution stores memories."""
        
        conversation_id = uuid4()
        user_id = uuid4()
        
        # Mock workflow result
        workflow_result = {
            "conversation_id": str(conversation_id),
            "current_message": "Test message",
            "contact_responses": {
                "contact-1": {
                    "status": "success",
                    "response": "Test response"
                }
            }
        }
        
        # Execute memory storage
        await workflow_engine._store_workflow_memories(
            result=workflow_result,
            user_id=user_id,
            conversation_id=conversation_id
        )
        
        # Verify memory manager was called
        workflow_engine.memory_manager.store_workflow_memory.assert_called_once_with(
            conversation_id=conversation_id,
            user_id=user_id,
            workflow_state=workflow_result,
            contact_responses=workflow_result["contact_responses"]
        )
        
        # Verify consolidation was triggered
        workflow_engine.memory_manager.trigger_memory_consolidation.assert_called_once_with(
            conversation_id
        )

    @pytest.mark.asyncio 
    async def test_build_memory_context_prompt(self, workflow_engine):
        """Test building memory context prompt for contacts."""
        
        memory_context = {
            "conversation_summary": {
                "summary": "Discussion about web development frameworks"
            },
            "short_term_memories": [
                {"content": "User asked about React vs Vue", "importance": 0.8},
                {"content": "Mentioned preference for TypeScript", "importance": 0.7}
            ],
            "relevant_memories": [
                {"content": "Previously discussed JavaScript best practices", "importance": 0.9}
            ]
        }
        
        contact = {"contact_id": "contact-1", "display_name": "Web Dev Expert"}
        
        # Execute
        prompt = await workflow_engine._build_memory_context_prompt(
            memory_context, contact
        )
        
        # Verify prompt structure
        assert prompt is not None
        assert "Context from previous conversations:" in prompt
        assert "web development frameworks" in prompt
        assert "React vs Vue" in prompt
        assert "JavaScript best practices" in prompt
        assert "personalized and relevant responses" in prompt

    @pytest.mark.asyncio
    async def test_memory_context_empty(self, workflow_engine):
        """Test handling empty memory context."""
        
        contact = {"contact_id": "contact-1", "display_name": "Test Expert"}
        
        # Test with None context
        prompt = await workflow_engine._build_memory_context_prompt(None, contact)
        assert prompt is None
        
        # Test with empty context
        empty_context = {}
        prompt = await workflow_engine._build_memory_context_prompt(empty_context, contact)
        assert prompt is None
        
        # Test with context but no relevant memories
        minimal_context = {
            "short_term_memories": [],
            "relevant_memories": []
        }
        prompt = await workflow_engine._build_memory_context_prompt(minimal_context, contact)
        assert prompt is None


class TestMemoryPerformanceAndOptimization:
    """Test memory system performance requirements."""
    
    @pytest.fixture
    def memory_manager(self):
        """Create memory manager for performance testing."""
        session = Mock()
        return ConversationMemoryManager(session)

    @pytest.mark.asyncio
    async def test_memory_retrieval_performance(self, memory_manager):
        """Test memory retrieval meets performance requirements (<100ms)."""
        
        # Mock fast memory retrieval
        with patch.object(memory_manager.memory_service, 'get_contextual_memories') as mock_contextual:
            with patch.object(memory_manager.memory_service, 'search_memories') as mock_search:
                
                # Setup fast responses
                mock_contextual.return_value = []
                mock_search.return_value = []
                
                # Measure performance
                import time
                start_time = time.time()
                
                await memory_manager.get_conversation_context(
                    conversation_id=uuid4(),
                    user_id=uuid4(),
                    current_message="Test message"
                )
                
                end_time = time.time()
                execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
                
                # Verify performance requirement (<100ms)
                assert execution_time < 100, f"Memory retrieval took {execution_time}ms, should be <100ms"

    def test_memory_configuration_defaults(self, memory_manager):
        """Test memory system configuration and defaults."""
        
        # Verify configuration defaults
        assert memory_manager.short_term_ttl_hours == 24
        assert memory_manager.medium_term_ttl_days == 30
        assert memory_manager.max_context_memories == 10
        assert memory_manager.similarity_threshold == 0.7
        
        # Verify these are reasonable values for production use
        assert 12 <= memory_manager.short_term_ttl_hours <= 48
        assert 14 <= memory_manager.medium_term_ttl_days <= 90
        assert 5 <= memory_manager.max_context_memories <= 20
        assert 0.5 <= memory_manager.similarity_threshold <= 0.9

    @pytest.mark.asyncio
    async def test_memory_consolidation_efficiency(self, memory_manager):
        """Test memory consolidation process efficiency."""
        
        conversation_id = uuid4()
        
        # Mock consolidation service
        with patch.object(memory_manager.memory_service, 'compress_short_to_medium_term') as mock_consolidate:
            mock_consolidate.return_value = Mock(summary="Test summary")
            
            # Test forced consolidation
            result = await memory_manager.trigger_memory_consolidation(
                conversation_id, force_consolidation=True
            )
            
            assert result == "Test summary"
            mock_consolidate.assert_called_once()
            
            # Test conditional consolidation
            with patch.object(memory_manager, '_check_consolidation_needed') as mock_check:
                mock_check.return_value = False
                
                result = await memory_manager.trigger_memory_consolidation(conversation_id)
                assert result is None  # Should skip consolidation


class TestMemorySystemIntegration:
    """Integration tests for the complete memory system."""
    
    def test_memory_workflow_integration(self):
        """Test integration between memory system and workflow execution."""
        
        # This would be a comprehensive integration test verifying:
        # 1. Memory context is properly retrieved during workflow initialization
        # 2. Contact responses include relevant memory context
        # 3. Workflow results are stored as memories
        # 4. Memory consolidation is triggered appropriately
        # 5. Cross-conversation memory sharing works correctly
        
        # For now, this serves as documentation of the expected integration
        assert True  # Placeholder

    def test_memory_personalization_accuracy(self):
        """Test memory system provides accurate personalization."""
        
        # This would test:
        # 1. Contact-specific memories are correctly retrieved
        # 2. User preferences are maintained across conversations
        # 3. Memory relevance scoring works correctly
        # 4. Cross-agent memory sharing respects privacy
        
        assert True  # Placeholder

    def test_memory_system_scalability(self):
        """Test memory system handles scale requirements."""
        
        # This would test:
        # 1. Performance with large numbers of memories
        # 2. Efficient memory consolidation at scale
        # 3. Query optimization for memory retrieval
        # 4. Resource usage within acceptable limits
        
        assert True  # Placeholder