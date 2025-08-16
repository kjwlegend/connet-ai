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


async def init_supabase() -> Optional[Client]:
    """Initialize Supabase client."""
    global _supabase_client
    
    settings = get_settings()
    
    # Skip Supabase initialization if URL or key are missing (development mode)
    if not settings.supabase_url or not settings.supabase_service_role_key:
        logger.warning("Supabase configuration missing - running in development mode without Supabase")
        _supabase_client = None
        return None
    
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
        
        # Skip client creation if configuration is missing
        if not settings.supabase_url or not settings.supabase_service_role_key:
            logger.warning("Supabase configuration missing - returning None")
            return None
            
        # For sync usage, create a new client
        _supabase_client = create_client(
            supabase_url=settings.supabase_url,
            supabase_key=settings.supabase_service_role_key,
        )
    
    return _supabase_client