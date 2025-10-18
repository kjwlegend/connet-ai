"""Cache key management and expiration policies."""

from typing import Optional


class CacheKeys:
    """Centralised cache key definitions."""

    USER_PREFIX = "user"
    USER_BY_ID = f"{USER_PREFIX}:id:{{user_id}}"
    USER_BY_EMAIL = f"{USER_PREFIX}:email:{{email}}"
    USER_BY_USERNAME = f"{USER_PREFIX}:username:{{username}}"
    USER_BY_INVITATION_CODE = f"{USER_PREFIX}:invite:{{code}}"
    USER_SESSIONS = f"{USER_PREFIX}:sessions:{{user_id}}"

    AUTH_PREFIX = "auth"
    JWT_BLACKLIST = f"{AUTH_PREFIX}:blacklist:{{token_id}}"
    LOGIN_ATTEMPTS = f"{AUTH_PREFIX}:attempts:{{email}}"
    PASSWORD_RESET = f"{AUTH_PREFIX}:reset:{{email}}"
    EMAIL_VERIFICATION = f"{AUTH_PREFIX}:verify:{{email}}"

    AGENT_PREFIX = "agent"
    AGENT_BY_ID = f"{AGENT_PREFIX}:id:{{agent_id}}"
    AGENT_BY_NAME = f"{AGENT_PREFIX}:name:{{name}}"
    AGENT_CAPABILITIES = f"{AGENT_PREFIX}:capabilities:{{agent_id}}"
    AGENT_KNOWLEDGE_BASE = f"{AGENT_PREFIX}:kb:{{agent_id}}"

    CONVERSATION_PREFIX = "conversation"
    CONVERSATION_BY_ID = f"{CONVERSATION_PREFIX}:id:{{conversation_id}}"
    CONVERSATION_PARTICIPANTS = (
        f"{CONVERSATION_PREFIX}:participants:{{conversation_id}}"
    )
    CONVERSATION_MESSAGES = (
        f"{CONVERSATION_PREFIX}:messages:{{conversation_id}}"
    )
    CONVERSATION_TOPICS = f"{CONVERSATION_PREFIX}:topics:{{conversation_id}}"

    MESSAGE_PREFIX = "message"
    MESSAGE_BY_ID = f"{MESSAGE_PREFIX}:id:{{message_id}}"
    MESSAGE_THREAD = f"{MESSAGE_PREFIX}:thread:{{thread_id}}"

    FILE_PREFIX = "file"
    FILE_BY_ID = f"{FILE_PREFIX}:id:{{file_id}}"
    FILE_PERMISSIONS = f"{FILE_PREFIX}:permissions:{{file_id}}"
    FILE_METADATA = f"{FILE_PREFIX}:metadata:{{file_id}}"

    CONTACT_PREFIX = "contact"
    USER_CONTACTS = f"{CONTACT_PREFIX}:user:{{user_id}}"
    CONTACT_REQUESTS = f"{CONTACT_PREFIX}:requests:{{user_id}}"

    TIMELINE_PREFIX = "timeline"
    USER_TIMELINE = f"{TIMELINE_PREFIX}:user:{{user_id}}"
    POST_BY_ID = f"{TIMELINE_PREFIX}:post:{{post_id}}"
    POST_COMMENTS = f"{TIMELINE_PREFIX}:comments:{{post_id}}"
    POST_LIKES = f"{TIMELINE_PREFIX}:likes:{{post_id}}"

    SEARCH_PREFIX = "search"
    SEARCH_RESULTS = f"{SEARCH_PREFIX}:results:{{query_hash}}"
    SEARCH_AGENTS = f"{SEARCH_PREFIX}:agents:{{query_hash}}"
    SEARCH_USERS = f"{SEARCH_PREFIX}:users:{{query_hash}}"

    SYSTEM_PREFIX = "system"
    SYSTEM_STATS = f"{SYSTEM_PREFIX}:stats"
    ONLINE_USERS = f"{SYSTEM_PREFIX}:online_users"
    ACTIVE_CONVERSATIONS = f"{SYSTEM_PREFIX}:active_conversations"

    RATE_LIMIT_PREFIX = "rate_limit"
    API_RATE_LIMIT = f"{RATE_LIMIT_PREFIX}:api:{{user_id}}:{{endpoint}}"
    LOGIN_RATE_LIMIT = f"{RATE_LIMIT_PREFIX}:login:{{ip_address}}"
    MESSAGE_RATE_LIMIT = f"{RATE_LIMIT_PREFIX}:message:{{user_id}}"

    @classmethod
    def user_by_id(cls, user_id: str) -> str:
        return cls.USER_BY_ID.format(user_id=user_id)

    @classmethod
    def user_by_email(cls, email: str) -> str:
        return cls.USER_BY_EMAIL.format(email=email)

    @classmethod
    def user_by_username(cls, username: str) -> str:
        return cls.USER_BY_USERNAME.format(username=username)

    @classmethod
    def user_by_invitation_code(cls, code: str) -> str:
        return cls.USER_BY_INVITATION_CODE.format(code=code)

    @classmethod
    def user_sessions(cls, user_id: str) -> str:
        return cls.USER_SESSIONS.format(user_id=user_id)

    @classmethod
    def jwt_blacklist(cls, token_id: str) -> str:
        return cls.JWT_BLACKLIST.format(token_id=token_id)

    @classmethod
    def login_attempts(cls, email: str) -> str:
        return cls.LOGIN_ATTEMPTS.format(email=email)

    @classmethod
    def conversation_by_id(cls, conversation_id: str) -> str:
        return cls.CONVERSATION_BY_ID.format(conversation_id=conversation_id)

    @classmethod
    def conversation_participants(cls, conversation_id: str) -> str:
        return cls.CONVERSATION_PARTICIPANTS.format(
            conversation_id=conversation_id
        )

    @classmethod
    def conversation_messages(
        cls, conversation_id: str, page: Optional[int] = None
    ) -> str:
        key = cls.CONVERSATION_MESSAGES.format(conversation_id=conversation_id)
        if page is not None:
            key += f":page:{page}"
        return key

    @classmethod
    def agent_by_id(cls, agent_id: str) -> str:
        return cls.AGENT_BY_ID.format(agent_id=agent_id)

    @classmethod
    def agent_capabilities(cls, agent_id: str) -> str:
        return cls.AGENT_CAPABILITIES.format(agent_id=agent_id)

    @classmethod
    def file_by_id(cls, file_id: str) -> str:
        return cls.FILE_BY_ID.format(file_id=file_id)

    @classmethod
    def user_contacts(cls, user_id: str) -> str:
        return cls.USER_CONTACTS.format(user_id=user_id)

    @classmethod
    def user_timeline(cls, user_id: str, page: Optional[int] = None) -> str:
        key = cls.USER_TIMELINE.format(user_id=user_id)
        if page is not None:
            key += f":page:{page}"
        return key

    @classmethod
    def search_results(cls, query_hash: str, page: Optional[int] = None) -> str:
        key = cls.SEARCH_RESULTS.format(query_hash=query_hash)
        if page is not None:
            key += f":page:{page}"
        return key

    @classmethod
    def api_rate_limit(cls, user_id: str, endpoint: str) -> str:
        return cls.API_RATE_LIMIT.format(user_id=user_id, endpoint=endpoint)

    @classmethod
    def message_rate_limit(cls, user_id: str) -> str:
        return cls.MESSAGE_RATE_LIMIT.format(user_id=user_id)


class CacheExpiration:
    """Cache expiration constants (seconds)."""

    VERY_SHORT = 60
    SHORT = 300
    MEDIUM = 900
    MEDIUM_LONG = 3600
    LONG = 7200
    VERY_LONG = 86400

    USER_SESSION = VERY_LONG
    USER_PROFILE = MEDIUM_LONG
    CONVERSATION = MEDIUM
    MESSAGES = SHORT
    AGENT_INFO = LONG
    SEARCH_RESULTS = MEDIUM
    FILE_METADATA = VERY_LONG
    RATE_LIMIT = SHORT
    JWT_BLACKLIST = VERY_LONG
    LOGIN_ATTEMPTS = MEDIUM_LONG


__all__ = ["CacheKeys", "CacheExpiration"]
