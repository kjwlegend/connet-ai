"""
Contacts Repository Implementation

This module provides the implementation of the Contacts repository.
"""
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from sqlmodel import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.contact_model import (
    ContactModel as Contact,
    ContactKnowledgeLink,
    ContactToolLink
)
from app.infrastructure.database.repositories.base_repository import BaseRepository
from app.utils.logging import get_logger

logger = get_logger(__name__)


class ContactRepository(BaseRepository[Contact]):
    """Contact Repository implementation."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Contact)
        
    async def get_by_follower_id(self, follower_id: UUID) -> Optional[Contact]:
        """Get contact by follower ID."""
        try:
            statement = select(Contact).where(Contact.follower_id == follower_id)
            result = await self.session.exec(statement)
            return result.first()
        except Exception as e:
            logger.error(f"Error getting contact by follower ID {follower_id}: {e}")
            raise
        
    async def get_by_following_id(self, following_id: UUID) -> Optional[Contact]:
        """Get contact by following ID."""
        try:
            statement = select(Contact).where(Contact.following_id == following_id)
            result = await self.session.exec(statement)
            return result.first()
        except Exception as e:
            logger.error(f"Error getting contact by following ID {following_id}: {e}")
            raise
        
    async def get_friends_list(self, follower_id: UUID) -> List[Contact]:
        """Get friends list for a follower."""
        try:
            statement = select(Contact).where(Contact.follower_id == follower_id, Contact.relationship_type == "friend")
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            logger.error(f"Error getting friends list for follower {follower_id}: {e}")
            raise

    async def get_blocked_list(self, follower_id: UUID) -> List[Contact]:
        """Get blocked list for a follower."""
        try:
            statement = select(Contact).where(Contact.follower_id == follower_id, Contact.relationship_type == "blocked")
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            logger.error(f"Error getting blocked list for follower {follower_id}: {e}")
            raise

    async def get_muted_list(self, follower_id: UUID) -> List[Contact]:
        """Get muted list for a follower."""
        try:
            statement = select(Contact).where(Contact.follower_id == follower_id, Contact.relationship_type == "muted")
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            logger.error(f"Error getting muted list for follower {follower_id}: {e}")
            raise

    async def get_favorite_list(self, follower_id: UUID) -> List[Contact]:
        """Get favorite list for a follower."""
        try:
            statement = select(Contact).where(Contact.follower_id == follower_id, Contact.relationship_type == "favorite")
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            logger.error(f"Error getting favorite list for follower {follower_id}: {e}")
            raise
    
    async def count_contacts(self, follower_id: UUID) -> int:
        """Count contacts for a follower."""
        try:
            statement = select(func.count(Contact.id)).where(Contact.follower_id == follower_id)
            result = await self.session.exec(statement)
            return result.scalar()
        except Exception as e:
            logger.error(f"Error counting contacts for follower {follower_id}: {e}")
            raise
    
    async def create_contact(self, contact: Contact) -> Contact:
        """Create a new contact."""
        try:
            self.session.add(contact)
            await self.session.commit()
            await self.session.refresh(contact)
            return self._model_to_entity(contact)
        except Exception as e:
            logger.error(f"Error creating contact: {e}")
            raise

    async def get_by_follower_username(self, follower_username: str) -> Optional[Contact]:
        """Get contact by follower username."""
        try:
            statement = select(Contact).where(Contact.follower_username == follower_username)
            result = await self.session.exec(statement)
            return result.first()
        except Exception as e:
            logger.error(f"Error getting contact by follower username {follower_username}: {e}")
            raise
        
    async def get_by_following_username(self, following_username: str) -> Optional[Contact]:
        """Get contact by following username."""
        try:
            statement = select(Contact).where(Contact.following_username == following_username)
            result = await self.session.exec(statement)
            return result.first()
        except Exception as e:
            logger.error(f"Error getting contact by following username {following_username}: {e}")
            raise
        
    async def update_contact(self, contact: Contact) -> Contact:
        """Update a contact.""" 
        try:
            stmt = select(Contact).where(Contact.id == contact.id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            if not model:
                return None
            for field, value in contact.model_dump().items():
                setattr(model, field, value)
            model.updated_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(model)

            logger.info(f"Contact updated successfully: {contact}")
            return self._model_to_entity(contact)
        
        except Exception as e:
            await self.session.rollback()
            logger.error(f"failed to update contact {contact} :{e}")

    async def delete_contact(self, contact_id: UUID) -> bool:
        """Delete a contact."""
        try:
            stmt = select(Contact).where(Contact.id == contact_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            if not model:
                return False
            await self.session.delete(model)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"failed to delete contact {contact_id} :{e}")
            return False
        
    async def exists(self, contact_id: UUID) -> bool:
        """Check if contact exists."""
        try:
            stmt = select(func.count(Contact.id)).where(Contact.id == contact_id)
            result = await self.session.execute(stmt)
            return result.scalar() > 0
        except Exception as e:
            logger.error(f"failed to check if contact {contact_id} exists :{e}")
            return False
        
    async def search_contacts(
            self,
            query: str,
            offset: int=0,
            limit: int = 20
    ) -> Tuple[List[Contact], int]:
        """Search contacts by name or email."""
        try:
            search_condition = or_(
                Contact.display_name.ilike(f"%{query}%"),
                Contact.email.ilike(f"%{query}%"),
                Contact.username.ilike(f"%{query}%") if Contact.username else False
            )
            stmt = select(Contact).where(search_condition).offset(offset).limit(limit)

            result = await self.session.exec(stmt)
            contacts = result.all()
            total_count = len(contacts)
            return contacts, total_count
        except Exception as e:
            logger.error(f"Error searching contacts: {e}")
            raise

    # Contact Knowledge Base Operations
    async def add_knowledge_to_contact(
        self,
        follower_id: UUID,
        following_id: UUID,
        following_type: str,
        knowledge_base_id: UUID,
        alias: Optional[str] = None
    ) -> ContactKnowledgeLink:
        """Add knowledge base to a contact."""
        try:
            knowledge_link = ContactKnowledgeLink(
                follower_id=follower_id,
                following_id=following_id,
                following_type=following_type,
                knowledge_base_id=knowledge_base_id,
                alias=alias
            )
            self.session.add(knowledge_link)
            await self.session.commit()
            await self.session.refresh(knowledge_link)
            return knowledge_link
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error adding knowledge to contact: {e}")
            raise

    async def remove_knowledge_from_contact(
        self,
        follower_id: UUID,
        following_id: UUID,
        following_type: str,
        knowledge_base_id: UUID
    ) -> bool:
        """Remove knowledge base from a contact."""
        try:
            stmt = select(ContactKnowledgeLink).where(
                and_(
                    ContactKnowledgeLink.follower_id == follower_id,
                    ContactKnowledgeLink.following_id == following_id,
                    ContactKnowledgeLink.following_type == following_type,
                    ContactKnowledgeLink.knowledge_base_id == knowledge_base_id
                )
            )
            result = await self.session.execute(stmt)
            knowledge_link = result.scalar_one_or_none()
            if knowledge_link:
                await self.session.delete(knowledge_link)
                await self.session.commit()
                return True
            return False
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error removing knowledge from contact: {e}")
            raise

    async def get_contact_knowledge_bases(
        self,
        follower_id: UUID,
        following_id: UUID,
        following_type: str
    ) -> List[ContactKnowledgeLink]:
        """Get all knowledge bases for a contact."""
        try:
            stmt = select(ContactKnowledgeLink).where(
                and_(
                    ContactKnowledgeLink.follower_id == follower_id,
                    ContactKnowledgeLink.following_id == following_id,
                    ContactKnowledgeLink.following_type == following_type
                )
            )
            result = await self.session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting contact knowledge bases: {e}")
            raise

    # Contact Tool Operations
    async def add_tool_to_contact(
        self,
        follower_id: UUID,
        following_id: UUID,
        following_type: str,
        tool_id: UUID,
        enabled: bool = True,
        tool_config: Optional[Dict[str, Any]] = None
    ) -> ContactToolLink:
        """Add tool to a contact."""
        try:
            tool_link = ContactToolLink(
                follower_id=follower_id,
                following_id=following_id,
                following_type=following_type,
                tool_id=tool_id,
                enabled=enabled,
                tool_config=tool_config
            )
            self.session.add(tool_link)
            await self.session.commit()
            await self.session.refresh(tool_link)
            return tool_link
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error adding tool to contact: {e}")
            raise

    async def remove_tool_from_contact(
        self,
        follower_id: UUID,
        following_id: UUID,
        following_type: str,
        tool_id: UUID
    ) -> bool:
        """Remove tool from a contact."""
        try:
            stmt = select(ContactToolLink).where(
                and_(
                    ContactToolLink.follower_id == follower_id,
                    ContactToolLink.following_id == following_id,
                    ContactToolLink.following_type == following_type,
                    ContactToolLink.tool_id == tool_id
                )
            )
            result = await self.session.execute(stmt)
            tool_link = result.scalar_one_or_none()
            if tool_link:
                await self.session.delete(tool_link)
                await self.session.commit()
                return True
            return False
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error removing tool from contact: {e}")
            raise

    async def get_contact_tools(
        self,
        follower_id: UUID,
        following_id: UUID,
        following_type: str
    ) -> List[ContactToolLink]:
        """Get all tools for a contact."""
        try:
            stmt = select(ContactToolLink).where(
                and_(
                    ContactToolLink.follower_id == follower_id,
                    ContactToolLink.following_id == following_id,
                    ContactToolLink.following_type == following_type
                )
            )
            result = await self.session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting contact tools: {e}")
            raise

    async def update_tool_config(
        self,
        follower_id: UUID,
        following_id: UUID,
        following_type: str,
        tool_id: UUID,
        enabled: Optional[bool] = None,
        tool_config: Optional[Dict[str, Any]] = None
    ) -> Optional[ContactToolLink]:
        """Update tool configuration for a contact."""
        try:
            stmt = select(ContactToolLink).where(
                and_(
                    ContactToolLink.follower_id == follower_id,
                    ContactToolLink.following_id == following_id,
                    ContactToolLink.following_type == following_type,
                    ContactToolLink.tool_id == tool_id
                )
            )
            result = await self.session.execute(stmt)
            tool_link = result.scalar_one_or_none()
            if tool_link:
                if enabled is not None:
                    tool_link.enabled = enabled
                if tool_config is not None:
                    tool_link.tool_config = tool_config
                await self.session.commit()
                await self.session.refresh(tool_link)
                return tool_link
            return None
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating tool config: {e}")
            raise
        