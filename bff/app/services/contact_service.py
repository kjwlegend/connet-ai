"""
Contact Service

This module provides Contact-related business logic.
"""

from typing import List, Optional, Tuple

from app.core.interfaces.repositories.user_repository import UserRepository
from app.infrastructure.cache.cache_keys import CacheKeys, CacheExpiration
from app.schemas.user import User, UserUpdateRequest
from app.services.base import BaseRepositoryService
from app.utils.logging import get_logger

logger = get_logger(__name__)
