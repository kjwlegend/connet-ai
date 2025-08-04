"""
JWT Authentication

This module provides JWT token management and authentication.
"""

from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any, Dict, List, Optional

from jose import JWTError, jwt

from app.config.settings import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


class JWTManager:
    """JWT token manager."""
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
    
    def create_access_token(
        self,
        subject: str,
        scopes: List[str] = None,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create access token."""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
            "scopes": scopes or [],
        }
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, subject: str) -> str:
        """Create refresh token."""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        to_encode = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
        }
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            raise ValueError(f"Invalid token: {str(e)}")
    
    async def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted."""
        # TODO: Implement token blacklisting with Redis
        return False


@lru_cache()
def get_jwt_manager() -> JWTManager:
    """Get JWT manager instance."""
    settings = get_settings()
    
    return JWTManager(
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
        access_token_expire_minutes=settings.access_token_expire_minutes,
        refresh_token_expire_days=settings.refresh_token_expire_days,
    )