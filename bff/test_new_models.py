#!/usr/bin/env python3
"""
Test script for the new data model extensions.
Verifies that the extended models work correctly.
"""

import asyncio
from datetime import datetime
from uuid import uuid4

from app.infrastructure.database.models import (
    AIAgentModel,
    ContactModel,
    ConversationParticipantModel,
    ConversationMemoryModel
)


def test_agent_model_extensions():
    """Test AIAgentModel with new LangGraph fields."""
    print("Testing AIAgentModel extensions...")
    
    agent = AIAgentModel(
        name="test_agent",
        display_name="Test Agent",
        description="A test agent",
        agent_type="custom",
        system_prompt="You are a test agent",
        created_by=uuid4(),
        
        # New fields
        node_type="workflow",
        execution_config={
            "timeout_seconds": 30,
            "max_retries": 3,
            "parallel_execution": True
        },
        resource_limits={
            "max_memory_mb": 512,
            "max_cpu_percent": 80,
            "max_execution_time": 60
        },
        dependencies={
            "required_tools": ["search", "calculator"],
            "optional_tools": ["image_generator"],
            "model_requirements": ["gpt-4", "claude-3"]
        }
    )
    
    print(f"Agent created with node_type: {agent.node_type}")
    print(f"Agent execution_config: {agent.execution_config}")
    print(f"Agent resource_limits: {agent.resource_limits}")
    print(f"Agent dependencies: {agent.dependencies}")
    

def test_contact_model_extensions():
    """Test ContactModel with new instance fields."""
    print("\nTesting ContactModel extensions...")
    
    contact = ContactModel(
        follower_id=uuid4(),
        following_id=uuid4(),
        following_type="agent",
        
        # New fields
        agent_id=uuid4(),
        custom_system_prompt="You are my personal assistant. Be concise and technical.",
        instance_config={
            "temperature": 0.7,
            "max_tokens": 2000,
            "model_preference": "gpt-4",
            "response_style": "technical"
        },
        resource_limits={
            "max_requests_per_hour": 100,
            "max_tokens_per_request": 4000
        }
    )
    
    print(f"Contact created with agent_id: {contact.agent_id}")
    print(f"Contact custom_system_prompt: {contact.custom_system_prompt[:50]}...")
    print(f"Contact instance_config: {contact.instance_config}")
    print(f"Contact resource_limits: {contact.resource_limits}")


def test_conversation_participant_extensions():
    """Test ConversationParticipantModel with new workflow fields."""
    print("\nTesting ConversationParticipantModel extensions...")
    
    participant = ConversationParticipantModel(
        conversation_id=uuid4(),
        participant_id=uuid4(),
        participant_type="agent",
        
        # New fields
        workflow_priority=10,
        conversation_permissions={
            "can_initiate_workflow": True,
            "can_modify_conversation": False,
            "can_access_memory": True,
            "allowed_tools": ["search", "calculation"]
        }
    )
    
    print(f"Participant created with workflow_priority: {participant.workflow_priority}")
    print(f"Participant conversation_permissions: {participant.conversation_permissions}")


def test_conversation_memory_model():
    """Test ConversationMemoryModel creation."""
    print("\nTesting ConversationMemoryModel...")
    
    memory = ConversationMemoryModel(
        conversation_id=uuid4(),
        participant_id=uuid4(),
        participant_type="user",
        memory_type="short_term",
        memory_category="user_preference",
        content="User prefers detailed code examples with explanations",
        context={
            "topic": "programming_help",
            "trigger_message": "Can you show me how to use async/await?",
            "conversation_turn": 5
        },
        importance_score=0.8,
        confidence_score=0.9,
        emotional_valence=0.2,
        embedding_model="text-embedding-ada-002",
        memory_metadata={
            "source": "explicit_statement",
            "extraction_method": "pattern_matching"
        }
    )
    
    print(f"Memory created with type: {memory.memory_type}")
    print(f"Memory category: {memory.memory_category}")
    print(f"Memory content: {memory.content[:50]}...")
    print(f"Memory importance_score: {memory.importance_score}")
    print(f"Memory context: {memory.context}")


def main():
    """Run all tests."""
    print("Testing Extended Data Models")
    print("=" * 50)
    
    try:
        test_agent_model_extensions()
        test_contact_model_extensions()
        test_conversation_participant_extensions()
        test_conversation_memory_model()
        
        print("\n" + "=" * 50)
        print("All model extension tests passed!")
        print("Data model extensions are working correctly!")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)