"""
Supabase Client

This module provides Supabase client configuration and management.
"""

from functools import lru_cache
from typing import Optional

from supabase import Client, create_client

from app.config.settings import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Global Supabase client instance
_supabase_client: Optional[Client] = None


async def init_supabase() -> Client:
    """Initialize Supabase client."""
    global _supabase_client
    
    settings = get_settings()
    
    _supabase_client = create_client(
        supabase_url=settings.supabase_url,
        supabase_key=settings.supabase_service_role_key,
    )
    
    logger.info("Supabase client initialized successfully")
    return _supabase_client


@lru_cache()
def get_supabase_client() -> Optional[Client]:
    """Get Supabase client instance."""
    global _supabase_client
    
    if _supabase_client is None:
        settings = get_settings()
        # For sync usage, create a new client
        _supabase_client = create_client(
            supabase_url=settings.supabase_url,
            supabase_key=settings.supabase_service_role_key,
        )
    
    return _supabase_client