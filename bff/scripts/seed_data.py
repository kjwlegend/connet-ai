#!/usr/bin/env python3
"""Seed the development database with representative data."""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List

from sqlmodel import select

from app.config.settings import get_settings
from app.core.db import get_async_session
from app.modules.ai.agents.models import AIAgentModel
from app.modules.ai.knowledge_bases.models import KnowledgeBaseModel
from app.modules.contacts.models import ContactModel, EntityType
from app.modules.conversations.messages.models import MessageModel
from app.modules.conversations.models import (
    ConversationModel,
    ConversationParticipantModel,
)
from app.modules.storage.files.models import FileModel
from app.modules.timeline.models import (
    TimelineCommentModel,
    TimelineLikeModel,
    TimelinePostModel,
)
from app.modules.users.invitations.models import UserInvitationModel
from app.modules.users.models import UserModel
from app.modules.users.registration.models import UserRegistrationSourceModel
from app.utils.logging import get_logger

logger = get_logger(__name__)

PASSWORD_HASH = (
    "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiRK6uA7rQz2"  # "password123"
)


class SeedDataManager:
    """Create or clear deterministic seed data for local development."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.created_entities: Dict[str, List[object]] = {
            "users": [],
            "agents": [],
            "conversations": [],
            "invitations": [],
            "timeline_posts": [],
            "files": [],
        }

    async def create_seed_data(self) -> None:
        """Populate the database with a consistent baseline dataset."""

        logger.info("Starting seed data creation…")

        async with get_async_session() as session:
            try:
                await self._create_users(session)
                await self._create_user_invitations(session)
                await self._create_registration_sources(session)
                await self._create_agents(session)
                await self._create_agent_knowledge_bases(session)
                await self._create_conversations(session)
                await self._create_messages(session)
                await self._create_contacts(session)
                await self._create_timeline_posts(session)
                await self._create_files(session)

                await session.commit()
                logger.info("Seed data creation completed successfully")

            except Exception as exc:  # pragma: no cover - diagnostic logging
                await session.rollback()
                logger.exception("Seed data creation failed: %s", exc)
                raise

    async def _create_users(self, session) -> None:
        """Create a handful of representative users."""

        logger.info("Creating test users…")

        users_data = [
            {
                "email": "admin@connet.ai",
                "full_name": "System Administrator",
                "username": "admin",
                "password_hash": PASSWORD_HASH,
                "invitation_code": "ADMIN-INVITE",
                "registration_source": "web",
                "registration_channel": "invite",
                "roles": ["admin"],
                "permissions": ["*"],
            },
            {
                "email": "alice@example.com",
                "full_name": "Alice Johnson",
                "username": "alice",
                "password_hash": PASSWORD_HASH,
                "registration_source": "web",
                "registration_channel": "organic",
                "roles": ["member"],
            },
            {
                "email": "bob@example.com",
                "full_name": "Bob Smith",
                "username": "bob",
                "password_hash": PASSWORD_HASH,
                "registration_source": "mobile",
                "registration_channel": "referral",
                "roles": ["member"],
            },
        ]

        for payload in users_data:
            user = UserModel(**payload)
            session.add(user)
            self.created_entities["users"].append(user)

        await session.flush()
        logger.info("Created %d users", len(users_data))

    async def _create_user_invitations(self, session) -> None:
        """Create invitations owned by the admin user."""

        if not self.created_entities["users"]:
            return

        admin_user = self.created_entities["users"][0]
        logger.info("Creating user invitations for %s", admin_user.email)

        invitations = [
            UserInvitationModel(
                code="WELCOME-2024",
                invited_by=admin_user.id,
                max_uses=10,
                expires_at=datetime.now(timezone.utc) + timedelta(days=120),
                invitation_type="beta",
                invitation_metadata={"audience": "early_access"},
            ),
            UserInvitationModel(
                code="TEAM-ACCESS",
                invited_by=admin_user.id,
                max_uses=5,
                expires_at=datetime.now(timezone.utc) + timedelta(days=60),
                invitation_type="team",
                invitation_metadata={"notes": "Internal collaboration"},
            ),
        ]

        for invitation in invitations:
            session.add(invitation)
            self.created_entities["invitations"].append(invitation)

        await session.flush()
        logger.info("Created %d invitations", len(invitations))

    async def _create_registration_sources(self, session) -> None:
        """Track how key users registered."""

        if len(self.created_entities["users"]) < 2:
            return

        logger.info("Creating registration source metadata…")

        alice, bob = self.created_entities["users"][1:3]

        sources = [
            UserRegistrationSourceModel(
                user_id=alice.id,
                source_type="web",
                source_detail="marketing_site",
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0)",
                ip_address="203.0.113.10",
                utm_data={
                    "utm_source": "google",
                    "utm_medium": "cpc",
                    "utm_campaign": "ai_collaboration",
                },
                referrer_url="https://www.google.com/",
            ),
            UserRegistrationSourceModel(
                user_id=bob.id,
                source_type="mobile",
                source_detail="ios_app",
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
                ip_address="198.51.100.22",
                utm_data={
                    "utm_source": "twitter",
                    "utm_medium": "social",
                    "utm_campaign": "product_launch",
                },
                referrer_url="https://t.co/product-launch",
            ),
        ]

        for source in sources:
            session.add(source)

        await session.flush()
        logger.info("Created %d registration source records", len(sources))

    async def _create_agents(self, session) -> None:
        """Create AI agents owned by the admin user."""

        if not self.created_entities["users"]:
            return

        admin_user = self.created_entities["users"][0]
        logger.info("Creating AI agents for %s", admin_user.email)

        agents = [
            AIAgentModel(
                name="code_assistant",
                display_name="Code Assistant",
                description="Specialised in code review and implementation guidance.",
                agent_type="assistant",
                system_prompt=(
                    "You are an expert software engineer helping users write high-quality code."
                ),
                created_by=admin_user.id,
                capabilities=["code_generation", "code_review"],
                tags=["engineering", "python"],
                personality_config={"tone": "helpful", "expertise": "senior"},
                model_preferences={"provider": "openai", "model": "gpt-4"},
            ),
            AIAgentModel(
                name="writing_helper",
                display_name="Writing Helper",
                description="Supports content planning, editing, and polishing.",
                agent_type="assistant",
                system_prompt="Provide concise, clear, and friendly writing assistance.",
                created_by=admin_user.id,
                capabilities=["editing", "content_strategy"],
                tags=["content", "writing"],
                personality_config={"tone": "encouraging"},
                model_preferences={"provider": "openai", "model": "gpt-4"},
            ),
        ]

        for agent in agents:
            session.add(agent)
            self.created_entities["agents"].append(agent)

        await session.flush()
        logger.info("Created %d agents", len(agents))

    async def _create_agent_knowledge_bases(self, session) -> None:
        """Attach small knowledge bases to the created agents."""

        if not self.created_entities["agents"]:
            return

        logger.info("Creating agent knowledge bases…")

        knowledge_bases = [
            KnowledgeBaseModel(
                name="python_best_practices",
                description="PEP-8 guidelines and idiomatic Python tips.",
                knowledge_type="documentation",
                owner_id=self.created_entities["users"][0].id,
                document_ids=[str(uuid.uuid4()) for _ in range(2)],
                tags=["python", "style"],
                knowledge_metadata={"language": "en"},
            ),
            KnowledgeBaseModel(
                name="writing_style_guide",
                description="Voice and tone guidance for marketing content.",
                knowledge_type="documentation",
                owner_id=self.created_entities["users"][0].id,
                tags=["writing", "style"],
                knowledge_metadata={"language": "en"},
            ),
        ]

        for kb in knowledge_bases:
            session.add(kb)

        await session.flush()
        logger.info("Created %d knowledge bases", len(knowledge_bases))

    async def _create_conversations(self, session) -> None:
        """Create sample conversations with participants."""

        if (
            len(self.created_entities["users"]) < 2
            or not self.created_entities["agents"]
        ):
            return

        logger.info("Creating conversations…")

        admin, alice = self.created_entities["users"][:2]
        code_assistant = self.created_entities["agents"][0]

        conversations = [
            ConversationModel(
                title="Python Code Review",
                conversation_type="direct",
                created_by=alice.id,
                is_group=False,
                status="active",
            ),
            ConversationModel(
                title="Roadmap Planning",
                conversation_type="group",
                created_by=admin.id,
                is_group=True,
                status="active",
            ),
        ]

        for conversation in conversations:
            session.add(conversation)
            self.created_entities["conversations"].append(conversation)

        await session.flush()

        participant_entries = [
            ConversationParticipantModel(
                conversation_id=conversations[0].id,
                participant_id=alice.id,
                participant_type="user",
                role="owner",
            ),
            ConversationParticipantModel(
                conversation_id=conversations[0].id,
                participant_id=code_assistant.id,
                participant_type="agent",
                role="assistant",
            ),
            ConversationParticipantModel(
                conversation_id=conversations[1].id,
                participant_id=admin.id,
                participant_type="user",
                role="owner",
            ),
            ConversationParticipantModel(
                conversation_id=conversations[1].id,
                participant_id=alice.id,
                participant_type="user",
                role="participant",
            ),
            ConversationParticipantModel(
                conversation_id=conversations[1].id,
                participant_id=code_assistant.id,
                participant_type="agent",
                role="assistant",
            ),
        ]

        for participant in participant_entries:
            session.add(participant)

        await session.flush()
        logger.info("Created %d conversation participants", len(participant_entries))

    async def _create_messages(self, session) -> None:
        """Add a few sample messages to the first conversation."""

        if not self.created_entities["conversations"]:
            return

        conversation = self.created_entities["conversations"][0]
        alice = self.created_entities["users"][1]
        code_assistant = self.created_entities["agents"][0]

        logger.info("Creating messages for conversation %s", conversation.title)

        messages = [
            MessageModel(
                conversation_id=conversation.id,
                sender_id=alice.id,
                sender_type="user",
                content="@code_assistant can you review my latest function?",
                message_type="text",
                agent_mentions=["code_assistant"],
            ),
            MessageModel(
                conversation_id=conversation.id,
                sender_id=code_assistant.id,
                sender_type="agent",
                content="Absolutely! Please share the snippet and I'll provide feedback.",
                message_type="text",
            ),
        ]

        for message in messages:
            session.add(message)

        await session.flush()
        logger.info("Created %d messages", len(messages))

    async def _create_contacts(self, session) -> None:
        """Create follow relationships between users and agents."""

        if (
            len(self.created_entities["users"]) < 2
            or not self.created_entities["agents"]
        ):
            return

        admin, alice = self.created_entities["users"][:2]
        code_assistant, writing_helper = self.created_entities["agents"]

        logger.info("Creating contact relationships…")

        contacts = [
            ContactModel(
                follower_id=admin.id,
                following_id=alice.id,
                following_type=EntityType.user,
                relationship_type="friend",
                tags=["team", "admin"],
            ),
            ContactModel(
                follower_id=alice.id,
                following_id=code_assistant.id,
                following_type=EntityType.agent,
                relationship_type="follow",
            ),
            ContactModel(
                follower_id=alice.id,
                following_id=writing_helper.id,
                following_type=EntityType.agent,
                relationship_type="follow",
            ),
        ]

        for contact in contacts:
            session.add(contact)

        await session.flush()
        logger.info("Created %d contacts", len(contacts))

    async def _create_timeline_posts(self, session) -> None:
        """Create timeline posts authored by users and agents."""

        if not self.created_entities["users"] or not self.created_entities["agents"]:
            return

        admin, alice = self.created_entities["users"][:2]
        code_assistant = self.created_entities["agents"][0]

        logger.info("Creating timeline posts…")

        posts = [
            TimelinePostModel(
                author_id=code_assistant.id,
                author_type="agent",
                title="Optimising Python workflows",
                content=(
                    "Just helped a teammate refactor their ETL job, cutting runtime by 40%. "
                    "Remember to profile and lean on list comprehensions!"
                ),
                visibility="public",
                category="public_square",
                tags=["python", "productivity"],
                hashtags=["#Python", "#Automation"],
            ),
            TimelinePostModel(
                author_id=alice.id,
                author_type="user",
                title="Sprint planning recap",
                content="Wrapped up sprint planning with new goals for the AI collaboration hub!",
                visibility="friends_circle",
                category="friends_circle",
                tags=["product", "planning"],
                hashtags=["#StartupLife"],
                mentioned_agents=[str(code_assistant.id)],
            ),
            TimelinePostModel(
                author_id=admin.id,
                author_type="user",
                title="Welcome new beta testers",
                content="Thrilled to welcome our latest beta testers. Share your feedback in the roadmap channel!",
                visibility="public",
                category="public_square",
                tags=["announcement"],
                hashtags=["#Community"],
                is_pinned=True,
            ),
        ]

        for post in posts:
            session.add(post)
            self.created_entities["timeline_posts"].append(post)

        await session.flush()
        logger.info("Created %d timeline posts", len(posts))

    async def _create_files(self, session) -> None:
        """Create file metadata linked to existing users."""

        if not self.created_entities["users"]:
            return

        admin, alice = self.created_entities["users"][:2]

        logger.info("Creating example files…")

        files = [
            FileModel(
                filename="project_requirements.md",
                display_name="Project Requirements",
                file_type="text/markdown",
                file_size=15_420,
                file_extension="md",
                storage_path="documents/project_requirements.md",
                storage_bucket="product-docs",
                uploaded_by=admin.id,
                is_public=False,
                tags=["planning"],
            ),
            FileModel(
                filename="sample_analysis.ipynb",
                display_name="Sample Analysis",
                file_type="application/x-ipynb+json",
                file_size=48_100,
                file_extension="ipynb",
                storage_path="notebooks/sample_analysis.ipynb",
                storage_bucket="analytics",
                uploaded_by=alice.id,
                is_public=False,
                tags=["analysis", "notebook"],
            ),
        ]

        for file_obj in files:
            session.add(file_obj)
            self.created_entities["files"].append(file_obj)

        await session.flush()
        logger.info("Created %d files", len(files))

    async def clear_existing_data(self) -> None:
        """Remove seed entities to start from a clean slate."""

        logger.info("Clearing existing seed data…")

        async with get_async_session() as session:
            try:
                tables_to_clear = [
                    TimelineLikeModel,
                    TimelineCommentModel,
                    TimelinePostModel,
                    MessageModel,
                    ConversationParticipantModel,
                    ConversationModel,
                    ContactModel,
                    FileModel,
                    KnowledgeBaseModel,
                    AIAgentModel,
                    UserRegistrationSourceModel,
                    UserInvitationModel,
                    UserModel,
                ]

                for table in tables_to_clear:
                    result = await session.exec(select(table))
                    for entity in result.all():
                        await session.delete(entity)

                await session.commit()
                logger.info("Existing seed data cleared successfully")

            except Exception as exc:  # pragma: no cover - diagnostic logging
                await session.rollback()
                logger.exception("Failed to clear existing seed data: %s", exc)
                raise


async def main() -> None:
    manager = SeedDataManager()

    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        await manager.clear_existing_data()
        print("✅ Existing seed data cleared")
        return

    try:
        await manager.create_seed_data()
        print("✅ Seed data created successfully")
        print("\nCreated entities:")
        for key, entities in manager.created_entities.items():
            print(f"  - {key}: {len(entities)}")
    except Exception as exc:  # pragma: no cover - surface failure to caller
        print(f"❌ Seed data creation failed: {exc}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
