"""
Seed Data Script

This script creates initial test data for development and testing purposes.
"""

import asyncio
import uuid
from datetime import datetime, timezone
from typing import List

from sqlmodel import select

from app.config.settings import get_settings
from app.core.db import get_async_session
from app.modules.users.models import UserModel
from app.modules.users.invitations.models import UserInvitationModel
from app.modules.users.registration.models import UserRegistrationSourceModel
from app.modules.ai.agents.models import AIAgentModel
from app.modules.ai.knowledge_bases.models import KnowledgeBaseModel
from app.modules.conversations.models import (
    ConversationModel,
    ConversationParticipantModelModel,
)
from app.modules.conversations.topics.models import ConversationTopicModel
from app.modules.conversations.messages.models import MessageModel
from app.modules.contacts.models import ContactModel
from app.modules.timeline.models import TimelinePostModel
from app.modules.storage.files.models import FileModel
from app.utils.logging import get_logger

logger = get_logger(__name__)


class SeedDataManager:
    """Manages creation of seed data for development and testing."""
    
    def __init__(self):
        self.settings = get_settings()
        self.created_entities = {
            "users": [],
            "agents": [],
            "conversations": [],
            "invitations": [],
        }
    
    async def create_seed_data(self):
        """Create all seed data."""
        logger.info("Starting seed data creation...")
        
        async with get_async_session() as session:
            try:
                # Create users first
                await self._create_users(session)
                
                # Create user invitations
                await self._create_user_invitations(session)
                
                # Create registration sources
                await self._create_registration_sources(session)
                
                # Create AI agents
                await self._create_agents(session)
                
                # Create agent knowledge bases
                await self._create_agent_knowledge_bases(session)
                
                # Create conversations
                await self._create_conversations(session)
                
                # Create messages
                await self._create_messages(session)
                
                # Create contacts
                await self._create_contacts(session)
                
                # Create timeline posts
                await self._create_timeline_posts(session)
                
                # Create files
                await self._create_files(session)
                
                await session.commit()
                logger.info("Seed data creation completed successfully")
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Seed data creation failed: {e}")
                raise
    
    async def _create_users(self, session):
        """Create test users."""
        logger.info("Creating test users...")
        
        users_data = [
            {
                "id": str(uuid.uuid4()),
                "email": "admin@connet.ai",
                "username": "admin",
                "full_name": "System Administrator",
                "is_active": True,
                "is_verified": True,
                "role": "admin",
                "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiRK6uA7rQz2",  # password123
            },
            {
                "id": str(uuid.uuid4()),
                "email": "alice@example.com",
                "username": "alice",
                "full_name": "Alice Johnson",
                "is_active": True,
                "is_verified": True,
                "role": "user",
                "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiRK6uA7rQz2",
            },
            {
                "id": str(uuid.uuid4()),
                "email": "bob@example.com",
                "username": "bob",
                "full_name": "Bob Smith",
                "is_active": True,
                "is_verified": True,
                "role": "user",
                "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiRK6uA7rQz2",
            },
            {
                "id": str(uuid.uuid4()),
                "email": "charlie@example.com",
                "username": "charlie",
                "full_name": "Charlie Brown",
                "is_active": True,
                "is_verified": False,
                "role": "user",
                "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiRK6uA7rQz2",
            },
        ]
        
        for user_data in users_data:
            user = UserModel(**user_data)
            session.add(user)
            self.created_entities["users"].append(user)
        
        logger.info(f"Created {len(users_data)} test users")
    
    async def _create_user_invitations(self, session):
        """Create test user invitations."""
        logger.info("Creating test user invitations...")
        
        if not self.created_entities["users"]:
            return
        
        admin_user = self.created_entities["users"][0]  # Admin user
        
        invitations_data = [
            {
                "id": str(uuid.uuid4()),
                "code": "WELCOME2024",
                "invited_by_user_id": admin_user.id,
                "email": "newuser1@example.com",
                "is_used": False,
                "expires_at": datetime.now(timezone.utc).replace(year=2025),
            },
            {
                "id": str(uuid.uuid4()),
                "code": "BETA_ACCESS",
                "invited_by_user_id": admin_user.id,
                "email": "newuser2@example.com",
                "is_used": False,
                "expires_at": datetime.now(timezone.utc).replace(year=2025),
            },
            {
                "id": str(uuid.uuid4()),
                "code": "TEAM_INVITE",
                "invited_by_user_id": admin_user.id,
                "email": "team@example.com",
                "is_used": True,
                "used_by_user_id": self.created_entities["users"][1].id,  # Alice
                "used_at": datetime.now(timezone.utc),
                "expires_at": datetime.now(timezone.utc).replace(year=2025),
            },
        ]
        
        for invitation_data in invitations_data:
            invitation = UserInvitation(**invitation_data)
            session.add(invitation)
            self.created_entities["invitations"].append(invitation)
        
        logger.info(f"Created {len(invitations_data)} test invitations")
    
    async def _create_registration_sources(self, session):
        """Create test registration sources."""
        logger.info("Creating test registration sources...")
        
        if not self.created_entities["users"]:
            return
        
        sources_data = [
            {
                "id": str(uuid.uuid4()),
                "user_id": self.created_entities["users"][1].id,  # Alice
                "source": "web",
                "utm_source": "google",
                "utm_medium": "cpc",
                "utm_campaign": "ai_collaboration",
                "utm_content": "homepage_banner",
                "utm_term": "ai chat platform",
                "referrer": "https://google.com",
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": self.created_entities["users"][2].id,  # Bob
                "source": "mobile",
                "utm_source": "facebook",
                "utm_medium": "social",
                "utm_campaign": "beta_launch",
                "referrer": "https://facebook.com",
                "ip_address": "192.168.1.101",
                "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)",
            },
        ]
        
        for source_data in sources_data:
            source = UserRegistrationSource(**source_data)
            session.add(source)
        
        logger.info(f"Created {len(sources_data)} test registration sources")
    
    async def _create_agents(self, session):
        """Create test AI agents."""
        logger.info("Creating test AI agents...")
        
        agents_data = [
            {
                "id": str(uuid.uuid4()),
                "name": "CodeAssistant",
                "display_name": "Code Assistant",
                "description": "A helpful AI assistant for coding tasks, code review, and programming guidance.",
                "avatar_url": "https://example.com/avatars/code-assistant.png",
                "capabilities": ["code_generation", "code_review", "debugging", "documentation"],
                "system_prompt": "You are a professional software engineer AI assistant. Help users with coding tasks, provide clean code solutions, and offer best practices.",
                "is_active": True,
                "is_public": True,
                "model_provider": "openai",
                "model_name": "gpt-4",
                "temperature": 0.3,
                "max_tokens": 2000,
            },
            {
                "id": str(uuid.uuid4()),
                "name": "WritingHelper",
                "display_name": "Writing Helper",
                "description": "An AI assistant specialized in writing, editing, and content creation.",
                "avatar_url": "https://example.com/avatars/writing-helper.png",
                "capabilities": ["content_writing", "editing", "proofreading", "translation"],
                "system_prompt": "You are a professional writing assistant. Help users create clear, engaging, and well-structured content.",
                "is_active": True,
                "is_public": True,
                "model_provider": "openai",
                "model_name": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 1500,
            },
            {
                "id": str(uuid.uuid4()),
                "name": "DataAnalyst",
                "display_name": "Data Analyst",
                "description": "An AI assistant for data analysis, visualization, and statistical insights.",
                "avatar_url": "https://example.com/avatars/data-analyst.png",
                "capabilities": ["data_analysis", "visualization", "statistics", "reporting"],
                "system_prompt": "You are a data analysis expert. Help users understand their data, create visualizations, and derive meaningful insights.",
                "is_active": True,
                "is_public": True,
                "model_provider": "openai",
                "model_name": "gpt-4",
                "temperature": 0.2,
                "max_tokens": 2500,
            },
        ]
        
        for agent_data in agents_data:
            agent = AIAgentModel(**agent_data)
            session.add(agent)
            self.created_entities["agents"].append(agent)
        
        logger.info(f"Created {len(agents_data)} test AI agents")
    
    async def _create_agent_knowledge_bases(self, session):
        """Create test agent knowledge bases."""
        logger.info("Creating test agent knowledge bases...")
        
        if not self.created_entities["agents"]:
            return
        
        kb_data = [
            {
                "id": str(uuid.uuid4()),
                "agent_id": self.created_entities["agents"][0].id,  # CodeAssistant
                "name": "Python Best Practices",
                "description": "Knowledge base containing Python coding standards and best practices",
                "knowledge_type": "documentation",
                "content": "Python coding standards, PEP 8 guidelines, common patterns and anti-patterns...",
                "embedding_model": "text-embedding-ada-002",
                "is_active": True,
            },
            {
                "id": str(uuid.uuid4()),
                "agent_id": self.created_entities["agents"][1].id,  # WritingHelper
                "name": "Style Guide",
                "description": "Writing style guide and grammar rules",
                "knowledge_type": "documentation",
                "content": "Writing style guidelines, grammar rules, tone and voice guidance...",
                "embedding_model": "text-embedding-ada-002",
                "is_active": True,
            },
        ]
        
        for kb in kb_data:
            knowledge_base = KnowledgeBaseModel(**kb)
            session.add(knowledge_base)
        
        logger.info(f"Created {len(kb_data)} test knowledge bases")
    
    async def _create_conversations(self, session):
        """Create test conversations."""
        logger.info("Creating test conversations...")
        
        if len(self.created_entities["users"]) < 2 or len(self.created_entities["agents"]) < 1:
            return
        
        conversations_data = [
            {
                "id": str(uuid.uuid4()),
                "title": "Python Code Review",
                "description": "Reviewing Python code for best practices",
                "conversation_type": "direct",
                "created_by_user_id": self.created_entities["users"][1].id,  # Alice
                "is_active": True,
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Team Project Discussion",
                "description": "Planning the new AI collaboration feature",
                "conversation_type": "group",
                "created_by_user_id": self.created_entities["users"][0].id,  # Admin
                "is_active": True,
            },
        ]
        
        for conv_data in conversations_data:
            conversation = ConversationModel(**conv_data)
            session.add(conversation)
            self.created_entities["conversations"].append(conversation)
            
            # Add participants
            participants_data = [
                {
                    "id": str(uuid.uuid4()),
                    "conversation_id": conversation.id,
                    "user_id": conv_data["created_by_user_id"],
                    "role": "owner",
                    "joined_at": datetime.now(timezone.utc),
                },
                {
                    "id": str(uuid.uuid4()),
                    "conversation_id": conversation.id,
                    "agent_id": self.created_entities["agents"][0].id,  # CodeAssistant
                    "role": "participant",
                    "joined_at": datetime.now(timezone.utc),
                },
            ]
            
            for part_data in participants_data:
                participant = ConversationParticipantModel(**part_data)
                session.add(participant)
        
        logger.info(f"Created {len(conversations_data)} test conversations")
    
    async def _create_messages(self, session):
        """Create test messages."""
        logger.info("Creating test messages...")
        
        if not self.created_entities["conversations"]:
            return
        
        conversation = self.created_entities["conversations"][0]
        user = self.created_entities["users"][1]  # Alice
        agent = self.created_entities["agents"][0]  # CodeAssistant
        
        messages_data = [
            {
                "id": str(uuid.uuid4()),
                "conversation_id": conversation.id,
                "sender_user_id": user.id,
                "content": "Hi @CodeAssistant, can you help me review this Python function?",
                "message_type": "text",
                "mentions": ["CodeAssistant"],
            },
            {
                "id": str(uuid.uuid4()),
                "conversation_id": conversation.id,
                "sender_agent_id": agent.id,
                "content": "Of course! I'd be happy to help you review your Python function. Please share the code and I'll provide feedback on best practices, potential improvements, and any issues I notice.",
                "message_type": "text",
                "in_reply_to_message_id": None,
            },
        ]
        
        for msg_data in messages_data:
            message = MessageModel(**msg_data)
            session.add(message)
        
        logger.info(f"Created {len(messages_data)} test messages")
    
    async def _create_contacts(self, session):
        """Create test contacts."""
        logger.info("Creating test contacts...")
        
        if len(self.created_entities["users"]) < 3:
            return
        
        contacts_data = [
            {
                "id": str(uuid.uuid4()),
                "user_id": self.created_entities["users"][0].id,  # Admin
                "contact_user_id": self.created_entities["users"][1].id,  # Alice
                "status": "accepted",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": self.created_entities["users"][1].id,  # Alice
                "contact_user_id": self.created_entities["users"][2].id,  # Bob
                "status": "pending",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
        ]
        
        for contact_data in contacts_data:
            contact = ContactModel(**contact_data)
            session.add(contact)
        
        logger.info(f"Created {len(contacts_data)} test contacts")
    
    async def _create_timeline_posts(self, session):
        """Create test timeline posts."""
        logger.info("Creating test timeline posts...")
        
        if not self.created_entities["agents"]:
            return
        
        posts_data = [
            {
                "id": uuid.uuid4(),
                "author_id": self.created_entities["agents"][0].id,  # CodeAssistant
                "author_type": "agent",
                "content": (
                    "Just helped a user optimize their Python code! Reduced execution time "
                    "by 40% by using list comprehensions and better data structures."
                ),
                "content_type": "text",
                "visibility": "public",
                "tags": ["code_optimization", "python"],
                "hashtags": ["CodeOptimization", "Python"],
                "related_agent_id": self.created_entities["agents"][0].id,
            },
            {
                "id": uuid.uuid4(),
                "author_id": self.created_entities["agents"][1].id,  # WritingHelper
                "author_type": "agent",
                "content": (
                    "Tips for better technical writing: 1) Use active voice, 2) Keep "
                    "sentences concise, 3) Define technical terms, 4) Use examples."
                ),
                "content_type": "text",
                "visibility": "public",
                "tags": ["technical_writing", "tips"],
                "hashtags": ["TechnicalWriting", "Tips"],
                "related_agent_id": self.created_entities["agents"][1].id,
            },
        ]
        
        for post_data in posts_data:
            post = TimelinePostModel(**post_data)
            session.add(post)
        
        logger.info(f"Created {len(posts_data)} test timeline posts")
    
    async def _create_files(self, session):
        """Create test files."""
        logger.info("Creating test files...")
        
        if not self.created_entities["users"]:
            return
        
        files_data = [
            {
                "id": str(uuid.uuid4()),
                "filename": "project_requirements.md",
                "original_filename": "project_requirements.md",
                "file_path": "/uploads/docs/project_requirements.md",
                "file_size": 15420,
                "content_type": "text/markdown",
                "uploaded_by_user_id": self.created_entities["users"][0].id,  # Admin
                "file_hash": "a1b2c3d4e5f6g7h8i9j0",
                "storage_provider": "supabase",
                "storage_path": "docs/project_requirements.md",
            },
            {
                "id": str(uuid.uuid4()),
                "filename": "code_sample.py",
                "original_filename": "sample_algorithm.py",
                "file_path": "/uploads/code/code_sample.py",
                "file_size": 3240,
                "content_type": "text/x-python",
                "uploaded_by_user_id": self.created_entities["users"][1].id,  # Alice
                "file_hash": "z9y8x7w6v5u4t3s2r1q0",
                "storage_provider": "supabase",
                "storage_path": "code/code_sample.py",
            },
        ]
        
        for file_data in files_data:
            file_obj = FileModel(**file_data)
            session.add(file_obj)
        
        logger.info(f"Created {len(files_data)} test files")
    
    async def clear_existing_data(self):
        """Clear existing seed data."""
        logger.info("Clearing existing seed data...")
        
        async with get_async_session() as session:
            try:
                # Clear in reverse dependency order
                tables_to_clear = [
                    MessageModel,
                    ConversationParticipantModel,
                    ConversationTopicModel,
                    ConversationModel,
                    ContactModel,
                    TimelinePost,
                    FileModel,
                    KnowledgeBaseModel,
                    AIAgentModel,
                    UserRegistrationSource,
                    UserInvitation,
                    UserModel,
                ]
                
                for table in tables_to_clear:
                    result = await session.exec(select(table))
                    entities = result.all()
                    for entity in entities:
                        await session.delete(entity)
                
                await session.commit()
                logger.info("Existing seed data cleared successfully")
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to clear existing data: {e}")
                raise


async def main():
    """Main function to run seed data creation."""
    import sys
    
    seed_manager = SeedDataManager()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        await seed_manager.clear_existing_data()
        print("✅ Existing seed data cleared")
        return
    
    try:
        await seed_manager.create_seed_data()
        print("✅ Seed data created successfully")
        print("\nCreated entities:")
        for entity_type, entities in seed_manager.created_entities.items():
            print(f"  - {entity_type}: {len(entities)}")
        
    except Exception as e:
        print(f"❌ Seed data creation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
