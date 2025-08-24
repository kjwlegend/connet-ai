"""
Cache Keys Management

This module defines and manages cache keys used throughout the application.
"""

from typing import Optional


class CacheKeys:
    """Centralized cache key management."""
    
    # User cache keys
    USER_PREFIX = "user"
    USER_BY_ID = f"{USER_PREFIX}:id:{{user_id}}"
    USER_BY_EMAIL = f"{USER_PREFIX}:email:{{email}}"
    USER_BY_USERNAME = f"{USER_PREFIX}:username:{{username}}"
    USER_BY_INVITATION_CODE = f"{USER_PREFIX}:invite:{{code}}"
    USER_SESSIONS = f"{USER_PREFIX}:sessions:{{user_id}}"
    
    # Authentication cache keys
    AUTH_PREFIX = "auth"
    JWT_BLACKLIST = f"{AUTH_PREFIX}:blacklist:{{token_id}}"
    LOGIN_ATTEMPTS = f"{AUTH_PREFIX}:attempts:{{email}}"
    PASSWORD_RESET = f"{AUTH_PREFIX}:reset:{{email}}"
    EMAIL_VERIFICATION = f"{AUTH_PREFIX}:verify:{{email}}"
    
    # Agent cache keys
    AGENT_PREFIX = "agent"
    AGENT_BY_ID = f"{AGENT_PREFIX}:id:{{agent_id}}"
    AGENT_BY_NAME = f"{AGENT_PREFIX}:name:{{name}}"
    AGENT_CAPABILITIES = f"{AGENT_PREFIX}:capabilities:{{agent_id}}"
    AGENT_KNOWLEDGE_BASE = f"{AGENT_PREFIX}:kb:{{agent_id}}"
    
    # Conversation cache keys
    CONVERSATION_PREFIX = "conversation"
    CONVERSATION_BY_ID = f"{CONVERSATION_PREFIX}:id:{{conversation_id}}"
    CONVERSATION_PARTICIPANTS = f"{CONVERSATION_PREFIX}:participants:{{conversation_id}}"
    CONVERSATION_MESSAGES = f"{CONVERSATION_PREFIX}:messages:{{conversation_id}}"
    CONVERSATION_TOPICS = f"{CONVERSATION_PREFIX}:topics:{{conversation_id}}"
    
    # Message cache keys
    MESSAGE_PREFIX = "message"
    MESSAGE_BY_ID = f"{MESSAGE_PREFIX}:id:{{message_id}}"
    MESSAGE_THREAD = f"{MESSAGE_PREFIX}:thread:{{thread_id}}"
    
    # File cache keys
    FILE_PREFIX = "file"
    FILE_BY_ID = f"{FILE_PREFIX}:id:{{file_id}}"
    FILE_PERMISSIONS = f"{FILE_PREFIX}:permissions:{{file_id}}"
    FILE_METADATA = f"{FILE_PREFIX}:metadata:{{file_id}}"
    
    # Contact cache keys
    CONTACT_PREFIX = "contact"
    USER_CONTACTS = f"{CONTACT_PREFIX}:user:{{user_id}}"
    CONTACT_REQUESTS = f"{CONTACT_PREFIX}:requests:{{user_id}}"
    
    # Timeline cache keys
    TIMELINE_PREFIX = "timeline"
    USER_TIMELINE = f"{TIMELINE_PREFIX}:user:{{user_id}}"
    POST_BY_ID = f"{TIMELINE_PREFIX}:post:{{post_id}}"
    POST_COMMENTS = f"{TIMELINE_PREFIX}:comments:{{post_id}}"
    POST_LIKES = f"{TIMELINE_PREFIX}:likes:{{post_id}}"
    
    # Search cache keys
    SEARCH_PREFIX = "search"
    SEARCH_RESULTS = f"{SEARCH_PREFIX}:results:{{query_hash}}"
    SEARCH_AGENTS = f"{SEARCH_PREFIX}:agents:{{query_hash}}"
    SEARCH_USERS = f"{SEARCH_PREFIX}:users:{{query_hash}}"
    
    # System cache keys
    SYSTEM_PREFIX = "system"
    SYSTEM_STATS = f"{SYSTEM_PREFIX}:stats"
    ONLINE_USERS = f"{SYSTEM_PREFIX}:online_users"
    ACTIVE_CONVERSATIONS = f"{SYSTEM_PREFIX}:active_conversations"
    
    # Rate limiting keys
    RATE_LIMIT_PREFIX = "rate_limit"
    API_RATE_LIMIT = f"{RATE_LIMIT_PREFIX}:api:{{user_id}}:{{endpoint}}"
    LOGIN_RATE_LIMIT = f"{RATE_LIMIT_PREFIX}:login:{{ip_address}}"
    MESSAGE_RATE_LIMIT = f"{RATE_LIMIT_PREFIX}:message:{{user_id}}"
    
    @classmethod
    def user_by_id(cls, user_id: str) -> str:
        """Get cache key for user by ID."""
        return cls.USER_BY_ID.format(user_id=user_id)
    
    @classmethod
    def user_by_email(cls, email: str) -> str:
        """Get cache key for user by email."""
        return cls.USER_BY_EMAIL.format(email=email)
    
    @classmethod
    def user_by_username(cls, username: str) -> str:
        """Get cache key for user by username."""
        return cls.USER_BY_USERNAME.format(username=username)
    
    @classmethod
    def user_by_invitation_code(cls, code: str) -> str:
        """Get cache key for user by invitation code."""
        return cls.USER_BY_INVITATION_CODE.format(code=code)
    
    @classmethod
    def user_sessions(cls, user_id: str) -> str:
        """Get cache key for user sessions."""
        return cls.USER_SESSIONS.format(user_id=user_id)
    
    @classmethod
    def jwt_blacklist(cls, token_id: str) -> str:
        """Get cache key for JWT blacklist."""
        return cls.JWT_BLACKLIST.format(token_id=token_id)
    
    @classmethod
    def login_attempts(cls, email: str) -> str:
        """Get cache key for login attempts."""
        return cls.LOGIN_ATTEMPTS.format(email=email)
    
    @classmethod
    def conversation_by_id(cls, conversation_id: str) -> str:
        """Get cache key for conversation by ID."""
        return cls.CONVERSATION_BY_ID.format(conversation_id=conversation_id)
    
    @classmethod
    def conversation_participants(cls, conversation_id: str) -> str:
        """Get cache key for conversation participants."""
        return cls.CONVERSATION_PARTICIPANTS.format(conversation_id=conversation_id)
    
    @classmethod
    def conversation_messages(cls, conversation_id: str, page: Optional[int] = None) -> str:
        """Get cache key for conversation messages."""
        key = cls.CONVERSATION_MESSAGES.format(conversation_id=conversation_id)
        if page is not None:
            key += f":page:{page}"
        return key
    
    @classmethod
    def agent_by_id(cls, agent_id: str) -> str:
        """Get cache key for agent by ID."""
        return cls.AGENT_BY_ID.format(agent_id=agent_id)
    
    @classmethod
    def agent_capabilities(cls, agent_id: str) -> str:
        """Get cache key for agent capabilities."""
        return cls.AGENT_CAPABILITIES.format(agent_id=agent_id)
    
    @classmethod
    def file_by_id(cls, file_id: str) -> str:
        """Get cache key for file by ID."""
        return cls.FILE_BY_ID.format(file_id=file_id)
    
    @classmethod
    def user_contacts(cls, user_id: str) -> str:
        """Get cache key for user contacts."""
        return cls.USER_CONTACTS.format(user_id=user_id)
    
    @classmethod
    def user_timeline(cls, user_id: str, page: Optional[int] = None) -> str:
        """Get cache key for user timeline."""
        key = cls.USER_TIMELINE.format(user_id=user_id)
        if page is not None:
            key += f":page:{page}"
        return key
    
    @classmethod
    def search_results(cls, query_hash: str, page: Optional[int] = None) -> str:
        """Get cache key for search results."""
        key = cls.SEARCH_RESULTS.format(query_hash=query_hash)
        if page is not None:
            key += f":page:{page}"
        return key
    
    @classmethod
    def api_rate_limit(cls, user_id: str, endpoint: str) -> str:
        """Get cache key for API rate limiting."""
        return cls.API_RATE_LIMIT.format(user_id=user_id, endpoint=endpoint)
    
    @classmethod
    def message_rate_limit(cls, user_id: str) -> str:
        """Get cache key for message rate limiting."""
        return cls.MESSAGE_RATE_LIMIT.format(user_id=user_id)


# Cache expiration times (in seconds)
class CacheExpiration:
    """Cache expiration time constants."""
    
    # Short-term cache (1-5 minutes)
    VERY_SHORT = 60          # 1 minute
    SHORT = 300              # 5 minutes
    
    # Medium-term cache (15-60 minutes)
    MEDIUM = 900             # 15 minutes
    MEDIUM_LONG = 3600       # 1 hour
    
    # Long-term cache (1-24 hours)
    LONG = 7200              # 2 hours
    VERY_LONG = 86400        # 24 hours
    
    # Specific cache durations
    USER_SESSION = VERY_LONG        # User session data
    USER_PROFILE = MEDIUM_LONG      # User profile info
    CONVERSATION = MEDIUM           # Conversation data
    MESSAGES = SHORT                # Message lists
    AGENT_INFO = LONG               # Agent information
    SEARCH_RESULTS = MEDIUM         # Search results
    FILE_METADATA = VERY_LONG       # File metadata
    RATE_LIMIT = SHORT              # Rate limiting windows
    JWT_BLACKLIST = VERY_LONG       # JWT token blacklist
    LOGIN_ATTEMPTS = MEDIUM_LONG    # Login attempt tracking