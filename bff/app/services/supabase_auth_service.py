"""
Supabase Authentication Service

This module integrates with Supabase Auth for user authentication,
while maintaining local user data in PostgreSQL.
"""

import json
import secrets
import string
import uuid
from datetime import datetime
from typing import Dict, Optional, Tuple

from gotrue.errors import AuthError
from supabase import Client

from app.core.interfaces.repositories.user_repository import UserRepository
from app.infrastructure.external.supabase.client import get_supabase_client
from app.schemas.user import User, UserCreate
from app.utils.logging import get_logger

logger = get_logger(__name__)


class SupabaseAuthService:
    """Supabase authentication service for integrating with Supabase Auth."""
    
    def __init__(
        self,
        user_repository: UserRepository,
        supabase_client: Optional[Client] = None,
    ):
        self.user_repository = user_repository
        self.supabase = supabase_client or get_supabase_client()
    
    def _generate_invitation_code(self) -> str:
        """Generate a unique invitation code."""
        # Format: 3 letters + 3 numbers (e.g., ABC123)
        letters = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(3))
        numbers = ''.join(secrets.choice(string.digits) for _ in range(3))
        return letters + numbers
    
    async def _ensure_unique_invitation_code(self) -> str:
        """Generate a unique invitation code that doesn't exist in database."""
        max_attempts = 10
        for _ in range(max_attempts):
            code = self._generate_invitation_code()
            # Check if code already exists
            existing_user = await self.user_repository.get_by_invitation_code(code)
            if not existing_user:
                return code
        
        # Fallback: use timestamp-based code if all random attempts fail
        import time
        timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
        return f"USR{timestamp}"
    
    async def register_user(
        self,
        email: str,
        password: str,
        full_name: str,
        username: Optional[str] = None,
        invited_by_code: Optional[str] = None,
        registration_source: Optional[str] = None,
        registration_channel: Optional[str] = None,
        utm_source: Optional[str] = None,
        utm_medium: Optional[str] = None,
        utm_campaign: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Tuple[User, Dict]:
        """
        Register a new user with Supabase Auth and sync to local database.
        
        Returns:
            Tuple of (local_user, supabase_auth_response)
        """
        try:
            # Check if user already exists locally
            existing_user = await self.user_repository.get_by_email(email)
            if existing_user:
                raise ValueError("User with this email already exists")
            
            if username:
                existing_username = await self.user_repository.get_by_username(username)
                if existing_username:
                    raise ValueError("Username already taken")
            
            # Validate invitation code if provided
            invited_by_user_id = None
            if invited_by_code:
                inviter = await self.user_repository.get_by_invitation_code(invited_by_code)
                if not inviter:
                    raise ValueError("Invalid invitation code")
                invited_by_user_id = inviter.id
            
            # Generate unique invitation code for new user
            invitation_code = await self._ensure_unique_invitation_code()
            
            # Prepare user metadata for Supabase
            user_metadata = {
                "full_name": full_name,
                "username": username,
                "invitation_code": invitation_code,
                "invited_by_code": invited_by_code,
                "registration_source": registration_source,
                "registration_channel": registration_channel,
                "utm_source": utm_source,
                "utm_medium": utm_medium,
                "utm_campaign": utm_campaign,
                **(metadata or {})
            }
            
            # Register with Supabase Auth
            auth_response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_metadata
                }
            })
            
            if auth_response.user is None:
                raise ValueError("Failed to create user in Supabase Auth")
            
            supabase_user = auth_response.user
            
            # Create local user record
            user_data = UserCreate(
                id=supabase_user.id,  # Use Supabase user ID
                email=email,
                full_name=full_name,
                username=username,
                is_active=not supabase_user.email_confirmed_at is None,  # Active if email confirmed
                auth_provider="supabase",
                external_id=supabase_user.id,
                invitation_code=invitation_code,
                invited_by_code=invited_by_code,
                invited_by_user_id=invited_by_user_id,
                registration_source=registration_source or "web",
                registration_channel=registration_channel or ("invite" if invited_by_code else "organic"),
                utm_source=utm_source,
                utm_medium=utm_medium,
                utm_campaign=utm_campaign,
                metadata=user_metadata,
            )
            
            local_user = await self.user_repository.create(user_data)
            
            logger.info(f"User registered successfully: {email} (ID: {supabase_user.id})")
            
            return local_user, {
                "user": supabase_user,
                "session": auth_response.session
            }
            
        except AuthError as e:
            logger.error(f"Supabase auth error during registration: {e}")
            raise ValueError(f"Registration failed: {e.message}")
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to register user {email}: {e}")
            raise
    
    async def login_user(
        self,
        email: str,
        password: str,
    ) -> Tuple[User, Dict]:
        """
        Authenticate user with Supabase Auth and return local user data.
        
        Returns:
            Tuple of (local_user, supabase_auth_response)
        """
        try:
            # Authenticate with Supabase
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user is None:
                raise ValueError("Authentication failed")
            
            supabase_user = auth_response.user
            
            # Get or sync local user
            local_user = await self._sync_user_from_supabase(supabase_user)
            
            # Update last login
            await self.user_repository.update_last_login(local_user.id)
            
            logger.info(f"User authenticated successfully: {email}")
            
            return local_user, {
                "user": supabase_user,
                "session": auth_response.session
            }
            
        except AuthError as e:
            logger.warning(f"Supabase auth error during login: {e}")
            raise ValueError("Invalid email or password")
        except Exception as e:
            logger.error(f"Failed to authenticate user {email}: {e}")
            raise
    
    async def refresh_session(self, refresh_token: str) -> Dict:
        """Refresh Supabase session."""
        try:
            auth_response = self.supabase.auth.refresh_session(refresh_token)
            
            if auth_response.user is None:
                raise ValueError("Failed to refresh session")
            
            # Sync user data
            await self._sync_user_from_supabase(auth_response.user)
            
            return {
                "user": auth_response.user,
                "session": auth_response.session
            }
            
        except AuthError as e:
            logger.error(f"Failed to refresh session: {e}")
            raise ValueError("Invalid refresh token")
    
    async def logout_user(self, access_token: str) -> bool:
        """Logout user from Supabase Auth."""
        try:
            # Set the session for logout
            self.supabase.auth.set_session(access_token, refresh_token="")
            
            # Sign out
            self.supabase.auth.sign_out()
            
            logger.info("User logged out successfully")
            return True
            
        except AuthError as e:
            logger.error(f"Failed to logout user: {e}")
            return False
    
    async def reset_password(self, email: str, redirect_to: Optional[str] = None) -> bool:
        """Send password reset email via Supabase Auth."""
        try:
            self.supabase.auth.reset_password_email(
                email=email,
                options={"redirect_to": redirect_to} if redirect_to else None
            )
            
            logger.info(f"Password reset email sent to: {email}")
            return True
            
        except AuthError as e:
            logger.error(f"Failed to send password reset email: {e}")
            return False
    
    async def update_user_password(
        self,
        user_id: str,
        new_password: str,
        access_token: str,
    ) -> bool:
        """Update user password in Supabase Auth."""
        try:
            # Set the session
            self.supabase.auth.set_session(access_token, refresh_token="")
            
            # Update password
            self.supabase.auth.update_user({
                "password": new_password
            })
            
            logger.info(f"Password updated for user: {user_id}")
            return True
            
        except AuthError as e:
            logger.error(f"Failed to update password: {e}")
            return False
    
    async def verify_email(self, token: str, email: str) -> bool:
        """Verify user email with Supabase Auth."""
        try:
            auth_response = self.supabase.auth.verify_otp({
                "email": email,
                "token": token,
                "type": "signup"
            })
            
            if auth_response.user:
                # Update local user status
                await self.user_repository.update_by_email(email, {"is_active": True})
                logger.info(f"Email verified for user: {email}")
                return True
            
            return False
            
        except AuthError as e:
            logger.error(f"Failed to verify email: {e}")
            return False
    
    async def get_user_from_token(self, access_token: str) -> Optional[User]:
        """Get user information from Supabase access token."""
        try:
            # Set the session
            self.supabase.auth.set_session(access_token, refresh_token="")
            
            # Get user from Supabase
            user_response = self.supabase.auth.get_user()
            
            if user_response.user is None:
                return None
            
            # Get local user
            local_user = await self.user_repository.get_by_id(user_response.user.id)
            
            if not local_user:
                # Sync user if not found locally
                local_user = await self._sync_user_from_supabase(user_response.user)
            
            return local_user
            
        except AuthError as e:
            logger.warning(f"Invalid access token: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to get user from token: {e}")
            return None
    
    async def get_oauth_url(
        self,
        provider: str,
        redirect_uri: str,
        state: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Generate OAuth authorization URL for the specified provider.
        
        Args:
            provider: OAuth provider (google, github)
            redirect_uri: Redirect URI for OAuth callback
            state: Optional state parameter for security
            
        Returns:
            Dictionary containing OAuth URL and state
        """
        try:
            # Generate state if not provided
            if not state:
                state = str(uuid.uuid4())
            
            # Map provider names to Supabase provider names
            provider_mapping = {
                "google": "google",
                "github": "github"
            }
            
            supabase_provider = provider_mapping.get(provider)
            if not supabase_provider:
                raise ValueError(f"Unsupported OAuth provider: {provider}")
            
            # Generate OAuth URL using Supabase
            auth_response = self.supabase.auth.sign_in_with_oauth({
                "provider": supabase_provider,
                "options": {
                    "redirect_to": redirect_uri,
                    "state": state,
                }
            })
            
            logger.info(f"Generated OAuth URL for provider: {provider}")
            
            return {
                "url": auth_response.url,
                "state": state
            }
            
        except Exception as e:
            logger.error(f"Failed to generate OAuth URL for {provider}: {e}")
            raise
    
    async def oauth_callback(
        self,
        provider: str,
        code: str,
        redirect_uri: str,
        state: Optional[str] = None,
    ) -> Tuple[User, Dict, bool]:
        """
        Handle OAuth callback and authenticate user.
        
        Args:
            provider: OAuth provider (google, github)
            code: OAuth authorization code
            redirect_uri: Redirect URI used in OAuth flow
            state: State parameter for security validation
            
        Returns:
            Tuple of (local_user, supabase_auth_response, is_new_user)
        """
        try:
            # Exchange code for session using Supabase
            auth_response = self.supabase.auth.exchange_code_for_session({
                "auth_code": code
            })
            
            if auth_response.user is None:
                raise ValueError("OAuth authentication failed")
            
            supabase_user = auth_response.user
            
            # Check if user already exists locally
            existing_user = await self.user_repository.get_by_id(supabase_user.id)
            is_new_user = existing_user is None
            
            # If new user, create local user record
            if is_new_user:
                # Extract user information from OAuth provider
                user_metadata = supabase_user.user_metadata or {}
                
                # Generate unique invitation code for new user
                invitation_code = await self._ensure_unique_invitation_code()
                
                # Determine username from OAuth data
                username = None
                if provider == "github":
                    username = user_metadata.get("user_name") or user_metadata.get("preferred_username")
                elif provider == "google":
                    # Google doesn't provide username, derive from email
                    email_prefix = supabase_user.email.split("@")[0] if supabase_user.email else None
                    if email_prefix:
                        # Check if email prefix is available as username
                        existing_username = await self.user_repository.get_by_username(email_prefix)
                        if not existing_username:
                            username = email_prefix
                
                # Create local user
                user_data = UserCreate(
                    id=supabase_user.id,
                    email=supabase_user.email,
                    full_name=user_metadata.get("full_name") or user_metadata.get("name", ""),
                    username=username,
                    is_active=True,  # OAuth users are immediately active
                    auth_provider=f"oauth_{provider}",
                    external_id=supabase_user.id,
                    invitation_code=invitation_code,
                    registration_source="oauth",
                    registration_channel=f"oauth_{provider}",
                    metadata={
                        **user_metadata,
                        "oauth_provider": provider,
                        "avatar_url": user_metadata.get("avatar_url"),
                    },
                )
                
                local_user = await self.user_repository.create(user_data)
                
                logger.info(f"New OAuth user created: {supabase_user.email} (provider: {provider})")
            else:
                # Update existing user
                local_user = await self._sync_user_from_supabase(supabase_user)
                
                # Update last login
                await self.user_repository.update_last_login(local_user.id)
                
                logger.info(f"Existing OAuth user authenticated: {supabase_user.email} (provider: {provider})")
            
            return local_user, {
                "user": supabase_user,
                "session": auth_response.session
            }, is_new_user
            
        except AuthError as e:
            logger.error(f"Supabase OAuth error: {e}")
            raise ValueError(f"OAuth authentication failed: {e.message}")
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"OAuth callback failed for {provider}: {e}")
            raise
    
    async def _sync_user_from_supabase(self, supabase_user) -> User:
        """Sync user data from Supabase to local database."""
        try:
            # Try to get existing local user
            local_user = await self.user_repository.get_by_id(supabase_user.id)
            
            # Extract metadata
            user_metadata = supabase_user.user_metadata or {}
            
            if local_user:
                # Update existing user
                update_data = {
                    "email": supabase_user.email,
                    "full_name": user_metadata.get("full_name", local_user.full_name),
                    "is_active": supabase_user.email_confirmed_at is not None,
                    "updated_at": datetime.utcnow(),
                    "metadata": user_metadata,
                }
                
                await self.user_repository.update(local_user.id, update_data)
                
                # Get updated user
                local_user = await self.user_repository.get_by_id(supabase_user.id)
            else:
                # Create new local user
                user_data = UserCreate(
                    id=supabase_user.id,
                    email=supabase_user.email,
                    full_name=user_metadata.get("full_name", ""),
                    username=user_metadata.get("username"),
                    is_active=supabase_user.email_confirmed_at is not None,
                    auth_provider="supabase",
                    external_id=supabase_user.id,
                    metadata=user_metadata,
                )
                
                local_user = await self.user_repository.create(user_data)
            
            return local_user
            
        except Exception as e:
            logger.error(f"Failed to sync user from Supabase: {e}")
            raise