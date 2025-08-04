"""
User Repository Implementation

This module provides the concrete implementation of the user repository.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.interfaces.repositories.user_repository import UserRepository
from app.infrastructure.database.models.user_model import UserModel
from app.schemas.user import User
from app.utils.logging import get_logger

logger = get_logger(__name__)


class UserRepositoryImpl(UserRepository):
    """User repository implementation using SQLModel."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        try:
            stmt = select(UserModel).where(UserModel.id == user_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            
            return self._model_to_entity(model) if model else None
            
        except Exception as e:
            logger.error(f"Failed to get user by ID {user_id}: {e}")
            raise
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        try:
            stmt = select(UserModel).where(UserModel.email == email)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            
            return self._model_to_entity(model) if model else None
            
        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {e}")
            raise
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        try:
            stmt = select(UserModel).where(UserModel.username == username)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            
            return self._model_to_entity(model) if model else None
            
        except Exception as e:
            logger.error(f"Failed to get user by username {username}: {e}")
            raise
    
    async def get_all(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[User]:
        """Get all users with pagination and filtering."""
        try:
            stmt = select(UserModel)
            
            # Apply filters if provided
            if filters:
                if "is_active" in filters:
                    stmt = stmt.where(UserModel.is_active == filters["is_active"])
            
            # Apply pagination
            stmt = stmt.offset(offset).limit(limit)
            
            # Order by creation date (newest first)
            stmt = stmt.order_by(UserModel.created_at.desc())
            
            result = await self.session.execute(stmt)
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            logger.error(f"Failed to get all users: {e}")
            raise
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count users with optional filtering."""
        try:
            stmt = select(func.count(UserModel.id))
            
            # Apply filters if provided
            if filters:
                if "is_active" in filters:
                    stmt = stmt.where(UserModel.is_active == filters["is_active"])
            
            result = await self.session.execute(stmt)
            return result.scalar()
            
        except Exception as e:
            logger.error(f"Failed to count users: {e}")
            raise
    
    async def create(self, user_data: Any) -> User:
        """Create a new user."""
        try:
            # Convert to model with support for external auth providers
            model_data = {
                "email": user_data.email,
                "full_name": user_data.full_name,
                "username": user_data.username,
                "is_active": getattr(user_data, 'is_active', True),
                "auth_provider": getattr(user_data, 'auth_provider', 'local'),
                "external_id": getattr(user_data, 'external_id', None),
                "invitation_code": getattr(user_data, 'invitation_code', None),
                "invited_by_code": getattr(user_data, 'invited_by_code', None),
                "invited_by_user_id": getattr(user_data, 'invited_by_user_id', None),
                "registration_source": getattr(user_data, 'registration_source', None),
                "registration_channel": getattr(user_data, 'registration_channel', None),
                "utm_source": getattr(user_data, 'utm_source', None),
                "utm_medium": getattr(user_data, 'utm_medium', None),
                "utm_campaign": getattr(user_data, 'utm_campaign', None),
                "metadata": getattr(user_data, 'metadata', None),
            }
            
            # Set ID if provided (for external auth providers)
            if hasattr(user_data, 'id') and user_data.id:
                model_data["id"] = user_data.id
            
            # Handle password vs password_hash
            if hasattr(user_data, 'password_hash') and user_data.password_hash:
                model_data["password_hash"] = user_data.password_hash
            elif hasattr(user_data, 'password') and user_data.password:
                model_data["password_hash"] = user_data.password
            
            model = UserModel(**model_data)
            
            self.session.add(model)
            await self.session.commit()
            await self.session.refresh(model)
            
            logger.info(f"User created successfully: {model.email}")
            return self._model_to_entity(model)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to create user: {e}")
            raise
    
    async def update(self, user_id: str, updates: Dict[str, Any]) -> Optional[User]:
        """Update a user."""
        try:
            # Get existing user
            stmt = select(UserModel).where(UserModel.id == user_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            
            if not model:
                return None
            
            # Apply updates
            for field, value in updates.items():
                if hasattr(model, field):
                    setattr(model, field, value)
            
            # Update timestamp
            model.updated_at = datetime.utcnow()
            
            await self.session.commit()
            await self.session.refresh(model)
            
            logger.info(f"User updated successfully: {user_id}")
            return self._model_to_entity(model)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to update user {user_id}: {e}")
            raise
    
    async def delete(self, user_id: str) -> bool:
        """Delete a user."""
        try:
            stmt = select(UserModel).where(UserModel.id == user_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            
            if not model:
                return False
            
            await self.session.delete(model)
            await self.session.commit()
            
            logger.info(f"User deleted successfully: {user_id}")
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to delete user {user_id}: {e}")
            raise
    
    async def exists(self, user_id: str) -> bool:
        """Check if user exists."""
        try:
            stmt = select(func.count(UserModel.id)).where(UserModel.id == user_id)
            result = await self.session.execute(stmt)
            count = result.scalar()
            
            return count > 0
            
        except Exception as e:
            logger.error(f"Failed to check user existence {user_id}: {e}")
            raise
    
    async def search_users(
        self,
        query: str,
        offset: int = 0,
        limit: int = 20
    ) -> Tuple[List[User], int]:
        """Search users by name or email."""
        try:
            # Build search condition
            search_condition = or_(
                UserModel.full_name.ilike(f"%{query}%"),
                UserModel.email.ilike(f"%{query}%"),
                UserModel.username.ilike(f"%{query}%") if UserModel.username else False
            )
            
            # Get total count
            count_stmt = select(func.count(UserModel.id)).where(search_condition)
            count_result = await self.session.execute(count_stmt)
            total = count_result.scalar()
            
            # Get users
            users_stmt = (
                select(UserModel)
                .where(search_condition)
                .offset(offset)
                .limit(limit)
                .order_by(UserModel.created_at.desc())
            )
            
            users_result = await self.session.execute(users_stmt)
            models = users_result.scalars().all()
            
            users = [self._model_to_entity(model) for model in models]
            
            return users, total
            
        except Exception as e:
            logger.error(f"Failed to search users with query '{query}': {e}")
            raise
    
    async def activate_user(self, user_id: str) -> bool:
        """Activate a user account."""
        try:
            return await self._update_user_status(user_id, True)
        except Exception as e:
            logger.error(f"Failed to activate user {user_id}: {e}")
            raise
    
    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account."""
        try:
            return await self._update_user_status(user_id, False)
        except Exception as e:
            logger.error(f"Failed to deactivate user {user_id}: {e}")
            raise
    
    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp."""
        try:
            stmt = select(UserModel).where(UserModel.id == user_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            
            if not model:
                return False
            
            model.last_login_at = datetime.utcnow()
            await self.session.commit()
            
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to update last login for user {user_id}: {e}")
            raise
    
    async def _update_user_status(self, user_id: str, is_active: bool) -> bool:
        """Update user active status."""
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            return False
        
        model.is_active = is_active
        model.updated_at = datetime.utcnow()
        
        await self.session.commit()
        
        action = "activated" if is_active else "deactivated"
        logger.info(f"User {action} successfully: {user_id}")
        
        return True
    
    async def update_by_email(self, email: str, update_data: dict) -> bool:
        """Update user by email address."""
        try:
            stmt = select(UserModel).where(UserModel.email == email)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            
            if not model:
                return False
            
            # Apply updates
            for field, value in update_data.items():
                if hasattr(model, field):
                    setattr(model, field, value)
            
            # Update timestamp
            model.updated_at = datetime.utcnow()
            
            await self.session.commit()
            
            logger.info(f"User updated by email successfully: {email}")
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to update user by email {email}: {e}")
            raise
    
    async def get_by_external_id(self, external_id: str, auth_provider: str) -> Optional[User]:
        """Get user by external ID and auth provider."""
        try:
            stmt = select(UserModel).where(
                UserModel.external_id == external_id,
                UserModel.auth_provider == auth_provider
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            
            return self._model_to_entity(model) if model else None
            
        except Exception as e:
            logger.error(f"Failed to get user by external ID {external_id}: {e}")
            raise
    
    async def get_by_invitation_code(self, invitation_code: str) -> Optional[User]:
        """Get user by invitation code."""
        try:
            stmt = select(UserModel).where(UserModel.invitation_code == invitation_code)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            
            return self._model_to_entity(model) if model else None
            
        except Exception as e:
            logger.error(f"Failed to get user by invitation code {invitation_code}: {e}")
            raise
    
    def _model_to_entity(self, model: UserModel) -> User:
        """Convert database model to domain entity."""
        return User(
            id=model.id,
            email=model.email,
            full_name=model.full_name,
            username=model.username,
            password_hash=model.password_hash,
            auth_provider=model.auth_provider,
            external_id=model.external_id,
            is_active=model.is_active,
            invitation_code=model.invitation_code,
            invited_by_code=model.invited_by_code,
            invited_by_user_id=model.invited_by_user_id,
            registration_source=model.registration_source,
            registration_channel=model.registration_channel,
            utm_source=model.utm_source,
            utm_medium=model.utm_medium,
            utm_campaign=model.utm_campaign,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login_at=model.last_login_at,
            permissions=model.permissions or [],
            roles=model.roles or [],
            metadata=model.metadata,
        )