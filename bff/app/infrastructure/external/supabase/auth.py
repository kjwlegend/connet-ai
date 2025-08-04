"""
Supabase Authentication Integration

This module provides additional Supabase authentication utilities
beyond the main auth service.
"""

from typing import Dict, Optional
from supabase import Client
from gotrue.errors import AuthError

from app.infrastructure.external.supabase.client import get_supabase_client
from app.utils.logging import get_logger

logger = get_logger(__name__)


class SupabaseAuthManager:
    """Extended Supabase authentication manager."""
    
    def __init__(self, client: Optional[Client] = None):
        self.client = client or get_supabase_client()
    
    async def create_user_with_metadata(
        self,
        email: str,
        password: str,
        metadata: Dict,
        email_confirm: bool = True
    ) -> Dict:
        """Create user with custom metadata in Supabase Auth."""
        try:
            response = self.client.auth.admin.create_user({
                "email": email,
                "password": password,
                "user_metadata": metadata,
                "email_confirm": email_confirm
            })
            
            logger.info(f"Created Supabase user: {email}")
            return response
            
        except AuthError as e:
            logger.error(f"Failed to create Supabase user: {e}")
            raise
    
    async def update_user_metadata(
        self,
        user_id: str,
        metadata: Dict
    ) -> Dict:
        """Update user metadata in Supabase Auth."""
        try:
            response = self.client.auth.admin.update_user_by_id(
                user_id,
                {"user_metadata": metadata}
            )
            
            logger.info(f"Updated Supabase user metadata: {user_id}")
            return response
            
        except AuthError as e:
            logger.error(f"Failed to update user metadata: {e}")
            raise
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user from Supabase Auth."""
        try:
            self.client.auth.admin.delete_user(user_id)
            logger.info(f"Deleted Supabase user: {user_id}")
            return True
            
        except AuthError as e:
            logger.error(f"Failed to delete user: {e}")
            return False
    
    async def list_users(
        self,
        page: int = 1,
        per_page: int = 20
    ) -> Dict:
        """List users from Supabase Auth."""
        try:
            response = self.client.auth.admin.list_users(
                page=page,
                per_page=per_page
            )
            
            return response
            
        except AuthError as e:
            logger.error(f"Failed to list users: {e}")
            raise
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID from Supabase Auth."""
        try:
            response = self.client.auth.admin.get_user_by_id(user_id)
            return response
            
        except AuthError as e:
            logger.warning(f"User not found in Supabase: {user_id}")
            return None
    
    async def send_password_reset_email(
        self,
        email: str,
        redirect_to: Optional[str] = None
    ) -> bool:
        """Send password reset email."""
        try:
            self.client.auth.reset_password_email(
                email,
                options={"redirect_to": redirect_to} if redirect_to else None
            )
            
            logger.info(f"Password reset email sent to: {email}")
            return True
            
        except AuthError as e:
            logger.error(f"Failed to send password reset email: {e}")
            return False
    
    async def invite_user_by_email(
        self,
        email: str,
        redirect_to: Optional[str] = None,
        data: Optional[Dict] = None
    ) -> Dict:
        """Invite user by email through Supabase Auth."""
        try:
            response = self.client.auth.admin.invite_user_by_email(
                email,
                options={
                    "redirect_to": redirect_to,
                    "data": data or {}
                }
            )
            
            logger.info(f"User invitation sent to: {email}")
            return response
            
        except AuthError as e:
            logger.error(f"Failed to invite user: {e}")
            raise


# Global instance
_supabase_auth_manager: Optional[SupabaseAuthManager] = None


def get_supabase_auth_manager() -> SupabaseAuthManager:
    """Get global Supabase auth manager instance."""
    global _supabase_auth_manager
    
    if _supabase_auth_manager is None:
        _supabase_auth_manager = SupabaseAuthManager()
    
    return _supabase_auth_manager