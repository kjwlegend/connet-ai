#!/usr/bin/env python3
"""
Database persistence test for extended models.
Tests that new fields can be properly saved and retrieved from the database.
"""

import asyncio
import os
from datetime import datetime
from uuid import uuid4

from sqlmodel import create_engine, SQLModel, Session

from app.infrastructure.database.models import (
    AIAgentModel,
    ContactModel,
    ConversationModel,
    ConversationParticipantModel,
    ConversationMemoryModel,
    UserModel
)


def test_database_persistence():
    """Test that extended models can be persisted to database."""
    
    # Use SQLite for testing
    sqlite_file = "test_extended_models.db"
    sqlite_url = f"sqlite:///{sqlite_file}"
    
    try:
        # Clean up any existing test database
        if os.path.exists(sqlite_file):
            os.remove(sqlite_file)
        
        engine = create_engine(sqlite_url)
        SQLModel.metadata.create_all(engine)
        
        print("Testing database persistence for extended models...")
        
        with Session(engine) as session:
            # 1. Create test user
            user = UserModel(
                email="test@example.com",
                full_name="Test User",
                auth_provider="email"
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            print(f"User created with ID: {user.id}")
            
            # 2. Test AIAgentModel with new fields
            agent = AIAgentModel(
                name="test_agent",
                display_name="Test Agent",
                description="A test agent",
                agent_type="custom",
                system_prompt="You are a test agent",
                created_by=user.id,
                
                # New LangGraph fields
                node_type="workflow",
                execution_config={
                    "timeout_seconds": 30,
                    "max_retries": 3,
                    "parallel_execution": True
                },
                resource_limits={
                    "max_memory_mb": 512,
                    "max_cpu_percent": 80
                },
                dependencies={
                    "required_tools": ["search", "calculator"]
                }
            )
            session.add(agent)
            session.commit()
            session.refresh(agent)
            print(f"Agent created with node_type: {agent.node_type}")
            
            # 3. Test ContactModel with new fields
            contact = ContactModel(
                follower_id=user.id,
                following_id=agent.id,
                following_type="agent",
                
                # New Contact instance fields
                agent_id=agent.id,
                custom_system_prompt="Be concise and technical",
                instance_config={
                    "temperature": 0.7,
                    "model_preference": "gpt-4"
                },
                resource_limits={
                    "max_requests_per_hour": 100
                }
            )
            session.add(contact)
            session.commit()
            session.refresh(contact)
            print(f"Contact created with agent_id: {contact.agent_id}")
            
            # 4. Create test conversation
            conversation = ConversationModel(
                title="Test Conversation",
                conversation_type="direct",
                status="active",
                created_by=user.id
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            print(f"Conversation created with ID: {conversation.id}")
            
            # 5. Test ConversationParticipantModel with new fields
            participant = ConversationParticipantModel(
                conversation_id=conversation.id,
                participant_id=agent.id,
                participant_type="agent",
                
                # New workflow fields
                workflow_priority=10,
                conversation_permissions={
                    "can_initiate_workflow": True,
                    "allowed_tools": ["search"]
                }
            )
            session.add(participant)
            session.commit()
            session.refresh(participant)
            print(f"Participant created with workflow_priority: {participant.workflow_priority}")
            
            # 6. Test ConversationMemoryModel
            memory = ConversationMemoryModel(
                conversation_id=conversation.id,
                participant_id=user.id,
                participant_type="user",
                memory_type="short_term",
                memory_category="user_preference",
                content="User prefers technical explanations",
                context={
                    "topic": "programming",
                    "confidence": 0.8
                },
                importance_score=0.7,
                confidence_score=0.9
            )
            session.add(memory)
            session.commit()
            session.refresh(memory)
            print(f"Memory created with type: {memory.memory_type}")
            
            print("\n=== Verifying retrieval ===")
            
            # Verify retrieval
            retrieved_agent = session.get(AIAgentModel, agent.id)
            assert retrieved_agent.node_type == "workflow"
            assert retrieved_agent.execution_config["timeout_seconds"] == 30
            print("Agent retrieval: PASSED")
            
            retrieved_contact = session.query(ContactModel).filter(
                ContactModel.follower_id == user.id,
                ContactModel.following_id == agent.id
            ).first()
            assert retrieved_contact.agent_id == agent.id
            assert retrieved_contact.instance_config["temperature"] == 0.7
            print("Contact retrieval: PASSED")
            
            retrieved_participant = session.query(ConversationParticipantModel).filter(
                ConversationParticipantModel.conversation_id == conversation.id,
                ConversationParticipantModel.participant_id == agent.id
            ).first()
            assert retrieved_participant.workflow_priority == 10
            assert retrieved_participant.conversation_permissions["can_initiate_workflow"] is True
            print("Participant retrieval: PASSED")
            
            retrieved_memory = session.get(ConversationMemoryModel, memory.id)
            assert retrieved_memory.memory_type == "short_term"
            assert retrieved_memory.context["topic"] == "programming"
            print("Memory retrieval: PASSED")
            
        print("\n" + "=" * 50)
        print("All database persistence tests passed!")
        print("Extended models work correctly with database!")
        
        return True
        
    except Exception as e:
        print(f"\nDatabase persistence test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up test database
        if os.path.exists(sqlite_file):
            os.remove(sqlite_file)


if __name__ == "__main__":
    success = test_database_persistence()
    exit(0 if success else 1)