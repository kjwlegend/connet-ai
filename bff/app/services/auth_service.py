"""
Authentication Service

This module provides authentication-related business logic.
"""

from functools import lru_cache
from typing import Optional

from passlib.context import CryptContext

from app.core.interfaces.repositories.user_repository import UserRepository
from app.infrastructure.cache.cache_manager import CacheManager
from app.schemas.user import User, UserCreate
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication service for user authentication logic."""
    
    def __init__(
        self,
        user_repository: UserRepository,
        cache_manager: CacheManager,
    ):
        self.user_repository = user_repository
        self.cache_manager = cache_manager
    
    async def register_user(
        self,
        email: str,
        password: str,
        full_name: str,
        username: Optional[str] = None,
    ) -> User:
        """Register a new user."""
        try:
            # Check if user already exists
            existing_user = await self.user_repository.get_by_email(email)
            if existing_user:
                raise ValueError("User with this email already exists")
            
            if username:
                existing_username = await self.user_repository.get_by_username(username)
                if existing_username:
                    raise ValueError("Username already taken")
            
            # Hash password
            password_hash = self.hash_password(password)
            
            # Create user
            user_data = UserCreate(
                email=email,
                password=password_hash,
                full_name=full_name,
                username=username,
            )
            
            user = await self.user_repository.create(user_data)
            
            logger.info(f"User registered successfully: {email}")
            return user
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to register user {email}: {e}")
            raise
    
    async def authenticate_user(
        self,
        email: str,
        password: str,
    ) -> Optional[User]:
        """Authenticate user with email and password."""
        try:
            # Get user by email
            user = await self.user_repository.get_by_email(email)
            
            if not user:
                logger.warning(f"Authentication failed: user not found for {email}")
                return None
            
            # Check if user is active
            if not user.is_active:
                logger.warning(f"Authentication failed: user {email} is inactive")
                return None
            
            # Verify password
            if not self.verify_password(password, user.password_hash):
                logger.warning(f"Authentication failed: invalid password for {email}")
                return None
            
            # Update last login
            await self.user_repository.update_last_login(user.id)
            
            logger.info(f"User authenticated successfully: {email}")
            return user
            
        except Exception as e:
            logger.error(f"Failed to authenticate user {email}: {e}")
            return None
    
    def hash_password(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    async def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str,
    ) -> bool:
        """Change user password."""
        try:
            # Get user
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Verify current password
            if not self.verify_password(current_password, user.password_hash):
                raise ValueError("Current password is incorrect")
            
            # Hash new password
            new_password_hash = self.hash_password(new_password)
            
            # Update password
            await self.user_repository.update(user_id, {"password_hash": new_password_hash})
            
            logger.info(f"Password changed for user: {user_id}")
            return True
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to change password for user {user_id}: {e}")
            raise


@lru_cache()
def get_auth_service() -> AuthService:
    """Get authentication service instance."""
    # This is a placeholder - in practice, you'd use dependency injection
    # to get the proper repository and cache manager instances
    from app.api.dependencies import get_user_repository, get_cache_manager
    
    # For now, return a basic instance
    # In production, this would be properly injected
    return AuthService(
        user_repository=None,  # Will be injected via dependencies
        cache_manager=None,    # Will be injected via dependencies
    )