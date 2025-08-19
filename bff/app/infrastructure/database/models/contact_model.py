"""
Contact Database Model

This module defines the SQLModel for contacts/following relationships in the database.
Supports users following other users or AI agents.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, TYPE_CHECKING
import enum
from uuid import UUID, uuid4

from sqlmodel import Column, Field, SQLModel, Text, select
from sqlalchemy import Column, JSON
from sqlalchemy import Enum as SAEnum
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    # Imported only for type hints to avoid circular imports at runtime
    from app.infrastructure.database.models.user_model import UserModel
    from app.infrastructure.database.models.agent_model import AIAgentModel


class EntityType(str, enum.Enum):
    user = "user"
    agent = "agent"


class ContactModel(SQLModel, table=True):
    """Contact/following relationship database model."""

    __tablename__ = "contacts"

    # 1) Identity (composite primary key = a directed edge A -> B with type)
    follower_id: UUID = Field(
        foreign_key="users.id",
        primary_key=True,
        description="Follower user ID (only users can follow)",
    )
    following_id: UUID = Field(
        primary_key=True, description="Following ID (user or agent being followed)"
    )
    following_type: EntityType = Field(
        description="Following type: user or agent",
        sa_column=Column(SAEnum(EntityType, name="entity_type")),
    )

    async def resolve_follower_username(self, session: AsyncSession) -> Optional[str]:
        """Return follower's username via DB lookup.
        Requires an explicit session to avoid implicit global state and polymorphic FK issues.
        """
        from app.infrastructure.database.models.user_model import (
            UserModel,
        )  # local import to avoid cycles

        result = await session.execute(
            select(UserModel.username).where(UserModel.id == self.follower_id)
        )
        return result.scalar_one_or_none()

    async def resolve_following_username(self, session: AsyncSession) -> Optional[str]:
        """Return following party's username (user or agent display handle)."""
        if self.following_type == EntityType.user:
            from app.infrastructure.database.models.user_model import UserModel

            result = await session.execute(
                select(UserModel.username).where(UserModel.id == self.following_id)
            )
            return result.scalar_one_or_none()
        else:
            # Agents may not have 'username'; use 'name' as handle
            from app.infrastructure.database.models.agent_model import AIAgentModel

            result = await session.execute(
                select(AIAgentModel.name).where(
                    AIAgentModel.id == self.following_id
                )
            )
            return result.scalar_one_or_none()

    async def resolve_follower_display_name(
        self, session: AsyncSession
    ) -> Optional[str]:
        """Return follower's display name (full_name for users)."""
        from app.infrastructure.database.models.user_model import UserModel

        result = await session.execute(
            select(UserModel.full_name).where(UserModel.id == self.follower_id)
        )
        return result.scalar_one_or_none()

    async def resolve_following_display_name(
        self, session: AsyncSession
    ) -> Optional[str]:
        """Return following party's display name (user.full_name or agent.display_name)."""
        if self.following_type == EntityType.user:
            from app.infrastructure.database.models.user_model import UserModel

            result = await session.execute(
                select(UserModel.full_name).where(UserModel.id == self.following_id)
            )
            return result.scalar_one_or_none()
        else:
            from app.infrastructure.database.models.agent_model import AIAgentModel

            result = await session.execute(
                select(AIAgentModel.display_name).where(
                    AIAgentModel.id == self.following_id
                )
            )
            return result.scalar_one_or_none()

    async def resolve_follower_email(self, session: AsyncSession) -> Optional[str]:
        """Return follower's email address."""
        from app.infrastructure.database.models.user_model import UserModel

        result = await session.execute(
            select(UserModel.email).where(UserModel.id == self.follower_id)
        )
        return result.scalar_one_or_none()

    async def resolve_following_email(self, session: AsyncSession) -> Optional[str]:
        """Return following party's email if user; agents typically have no email, returns None."""
        if self.following_type == EntityType.user:
            from app.infrastructure.database.models.user_model import UserModel

            result = await session.execute(
                select(UserModel.email).where(UserModel.id == self.following_id)
            )
            return result.scalar_one_or_none()
        return None

    # 2) Relationship semantics
    relationship_type: str = Field(
        default="follow",
        max_length=20,
        description="Relationship type: follow, friend, blocked, muted",
    )

    # 3) Relationship presentation
    display_name: Optional[str] = Field(
        default=None, max_length=100, description="Custom display name for this contact"
    )
    notes: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description="Personal notes about this contact",
    )
    tags: List[str] = Field(
        default=[],
        description="Custom tags for organization",
        sa_column=Column(JSON),
    )

    # 4) Status flags
    is_favorite: bool = Field(
        default=False, description="Whether this is a favorite contact"
    )
    is_muted: bool = Field(default=False, description="Whether notifications are muted")
    is_blocked: bool = Field(
        default=False, description="Whether this contact is blocked"
    )

    # 5) Presence tracking
    online_status: str = Field(
        default="unknown",
        max_length=20,
        description="Online status: online, offline, away, busy, unknown",
    )
    last_seen_at: Optional[datetime] = Field(
        default=None, description="Last seen timestamp"
    )

    # 6) Agent semantics (contact-scoped)
    # Whether this contact should behave as an agent entry point (a real user can be delegated as agent)
    is_agent: bool = Field(
        default=False,
        description="Whether the followed user is delegated to act as an agent for this follower",
    )

    # 7) View conveniences
    is_pinned: bool = Field(
        default=False, description="Pinned contact for quick access"
    )
    pin_order: int = Field(
        default=0, description="Ordering index among pinned contacts"
    )
    is_archived: bool = Field(
        default=False, description="Archived contact (hidden from default views)"
    )

    # 8) QR code feature for easy contact addition
    qr_code_shared: bool = Field(
        default=False, description="Whether contact was added via QR code"
    )
    shared_via: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Method contact was shared: qr_code, invite_link, search, etc.",
    )

    # 9) Notification settings
    notification_level: str = Field(
        default="normal",
        max_length=20,
        description="Notification level: none, important, normal, all",
    )

    # 10) Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Relationship creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )
    last_interaction_at: Optional[datetime] = Field(
        default=None, description="Last interaction timestamp"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "follower_id": "12345678-1234-5678-9012-123456789012",
                "following_id": "87654321-4321-8765-2109-876543210987",
                "following_type": "agent",
                "relationship_type": "follow",
                "display_name": "My Code Assistant",
                "notes": "Great for debugging Python issues",
                "tags": ["coding", "helpful", "technical"],
                "is_favorite": True,
                "is_muted": False,
                "notification_level": "all",
                "online_status": "online",
                "is_agent": True,
                "is_pinned": True,
                "pin_order": 1,
            }
        }
    }


class ContactKnowledgeLink(SQLModel, table=True):
    """Per-contact assignment of knowledge bases (scoped to the directed edge)."""

    __tablename__ = "contact_knowledge_links"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    # Contact scope (no strict FK to composite PK; enforced at service or via custom constraints)
    follower_id: UUID = Field(foreign_key="users.id", index=True)
    following_id: UUID = Field(index=True)
    following_type: EntityType = Field(
        sa_column=Column(SAEnum(EntityType, name="entity_type"))
    )

    knowledge_base_id: UUID = Field(foreign_key="knowledge_database.id")
    alias: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Optional alias for this KB in contact context",
    )
    added_at: datetime = Field(default_factory=datetime.utcnow)


class ContactToolLink(SQLModel, table=True):
    """Per-contact assignment of tools with optional config overrides."""

    __tablename__ = "contact_tool_links"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    # Contact scope
    follower_id: UUID = Field(foreign_key="users.id", index=True)
    following_id: UUID = Field(index=True)
    following_type: EntityType = Field(
        sa_column=Column(SAEnum(EntityType, name="entity_type"))
    )

    tool_id: UUID = Field(foreign_key="tools.id")
    enabled: bool = Field(default=True)
    tool_config: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    added_at: datetime = Field(default_factory=datetime.utcnow)
