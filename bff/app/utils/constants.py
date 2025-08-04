"""
Application Constants

This module defines constants used throughout the application.
"""

from enum import Enum
from typing import Dict, List


# API Constants
class APIConstants:
    """API-related constants."""
    
    # API versioning
    API_V1_PREFIX = "/api/v1"
    
    # Default pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    DEFAULT_OFFSET = 0
    
    # Rate limiting
    DEFAULT_RATE_LIMIT = 100  # requests per minute
    AUTH_RATE_LIMIT = 5      # login attempts per minute
    MESSAGE_RATE_LIMIT = 30  # messages per minute
    
    # Request timeouts (seconds)
    DEFAULT_TIMEOUT = 30
    UPLOAD_TIMEOUT = 300
    AI_REQUEST_TIMEOUT = 60


# User Constants
class UserConstants:
    """User-related constants."""
    
    # User roles
    ROLE_ADMIN = "admin"
    ROLE_USER = "user"
    ROLE_MODERATOR = "moderator"
    ROLE_GUEST = "guest"
    
    VALID_ROLES = [ROLE_ADMIN, ROLE_USER, ROLE_MODERATOR, ROLE_GUEST]
    
    # User status
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_SUSPENDED = "suspended"
    STATUS_DELETED = "deleted"
    
    VALID_STATUSES = [STATUS_ACTIVE, STATUS_INACTIVE, STATUS_SUSPENDED, STATUS_DELETED]
    
    # Username constraints
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 50
    
    # Password constraints
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    
    # Name constraints
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 100
    
    # Registration sources
    REGISTRATION_WEB = "web"
    REGISTRATION_MOBILE = "mobile"
    REGISTRATION_API = "api"
    REGISTRATION_ADMIN = "admin"
    
    VALID_REGISTRATION_SOURCES = [
        REGISTRATION_WEB,
        REGISTRATION_MOBILE,
        REGISTRATION_API,
        REGISTRATION_ADMIN
    ]


# Agent Constants
class AgentConstants:
    """Agent-related constants."""
    
    # Agent types
    TYPE_CHAT = "chat"
    TYPE_TASK = "task"
    TYPE_SPECIALIST = "specialist"
    TYPE_PLANNER = "planner"
    
    VALID_AGENT_TYPES = [TYPE_CHAT, TYPE_TASK, TYPE_SPECIALIST, TYPE_PLANNER]
    
    # Agent capabilities
    CAPABILITY_CODE_GENERATION = "code_generation"
    CAPABILITY_CODE_REVIEW = "code_review"
    CAPABILITY_DEBUGGING = "debugging"
    CAPABILITY_DOCUMENTATION = "documentation"
    CAPABILITY_CONTENT_WRITING = "content_writing"
    CAPABILITY_EDITING = "editing"
    CAPABILITY_TRANSLATION = "translation"
    CAPABILITY_DATA_ANALYSIS = "data_analysis"
    CAPABILITY_VISUALIZATION = "visualization"
    CAPABILITY_RESEARCH = "research"
    CAPABILITY_PLANNING = "planning"
    CAPABILITY_TASK_MANAGEMENT = "task_management"
    
    VALID_CAPABILITIES = [
        CAPABILITY_CODE_GENERATION,
        CAPABILITY_CODE_REVIEW,
        CAPABILITY_DEBUGGING,
        CAPABILITY_DOCUMENTATION,
        CAPABILITY_CONTENT_WRITING,
        CAPABILITY_EDITING,
        CAPABILITY_TRANSLATION,
        CAPABILITY_DATA_ANALYSIS,
        CAPABILITY_VISUALIZATION,
        CAPABILITY_RESEARCH,
        CAPABILITY_PLANNING,
        CAPABILITY_TASK_MANAGEMENT,
    ]
    
    # Model providers
    PROVIDER_OPENAI = "openai"
    PROVIDER_ANTHROPIC = "anthropic"
    PROVIDER_GOOGLE = "google"
    PROVIDER_AZURE = "azure"
    PROVIDER_HUGGINGFACE = "huggingface"
    
    VALID_PROVIDERS = [
        PROVIDER_OPENAI,
        PROVIDER_ANTHROPIC,
        PROVIDER_GOOGLE,
        PROVIDER_AZURE,
        PROVIDER_HUGGINGFACE,
    ]
    
    # Agent constraints
    MIN_AGENT_NAME_LENGTH = 3
    MAX_AGENT_NAME_LENGTH = 50
    MIN_DISPLAY_NAME_LENGTH = 3
    MAX_DISPLAY_NAME_LENGTH = 100
    MAX_DESCRIPTION_LENGTH = 500
    MAX_SYSTEM_PROMPT_LENGTH = 5000
    
    # Model configuration limits
    MIN_TEMPERATURE = 0.0
    MAX_TEMPERATURE = 2.0
    MIN_MAX_TOKENS = 1
    MAX_MAX_TOKENS = 8000


# Conversation Constants
class ConversationConstants:
    """Conversation-related constants."""
    
    # Conversation types
    TYPE_DIRECT = "direct"
    TYPE_GROUP = "group"
    TYPE_CHANNEL = "channel"
    TYPE_BROADCAST = "broadcast"
    
    VALID_CONVERSATION_TYPES = [TYPE_DIRECT, TYPE_GROUP, TYPE_CHANNEL, TYPE_BROADCAST]
    
    # Participant roles
    ROLE_OWNER = "owner"
    ROLE_ADMIN = "admin"
    ROLE_MODERATOR = "moderator"
    ROLE_PARTICIPANT = "participant"
    ROLE_OBSERVER = "observer"
    
    VALID_PARTICIPANT_ROLES = [
        ROLE_OWNER,
        ROLE_ADMIN,
        ROLE_MODERATOR,
        ROLE_PARTICIPANT,
        ROLE_OBSERVER,
    ]
    
    # Conversation constraints
    MAX_TITLE_LENGTH = 200
    MAX_DESCRIPTION_LENGTH = 1000
    MAX_PARTICIPANTS = 100
    MAX_DIRECT_PARTICIPANTS = 2


# Message Constants
class MessageConstants:
    """Message-related constants."""
    
    # Message types
    TYPE_TEXT = "text"
    TYPE_IMAGE = "image"
    TYPE_FILE = "file"
    TYPE_CODE = "code"
    TYPE_SYSTEM = "system"
    TYPE_AUDIO = "audio"
    TYPE_VIDEO = "video"
    
    VALID_MESSAGE_TYPES = [
        TYPE_TEXT,
        TYPE_IMAGE,
        TYPE_FILE,
        TYPE_CODE,
        TYPE_SYSTEM,
        TYPE_AUDIO,
        TYPE_VIDEO,
    ]
    
    # Message constraints
    MAX_CONTENT_LENGTH = 10000
    MAX_MENTIONS = 10
    MAX_ATTACHMENTS = 5
    
    # System message types
    SYSTEM_USER_JOINED = "user_joined"
    SYSTEM_USER_LEFT = "user_left"
    SYSTEM_AGENT_ADDED = "agent_added"
    SYSTEM_AGENT_REMOVED = "agent_removed"
    SYSTEM_CONVERSATION_CREATED = "conversation_created"
    SYSTEM_CONVERSATION_ARCHIVED = "conversation_archived"


# File Constants
class FileConstants:
    """File-related constants."""
    
    # File types
    TYPE_IMAGE = "image"
    TYPE_DOCUMENT = "document"
    TYPE_CODE = "code"
    TYPE_AUDIO = "audio"
    TYPE_VIDEO = "video"
    TYPE_ARCHIVE = "archive"
    TYPE_OTHER = "other"
    
    # Allowed image formats
    ALLOWED_IMAGE_FORMATS = [
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "image/svg+xml",
    ]
    
    # Allowed document formats
    ALLOWED_DOCUMENT_FORMATS = [
        "application/pdf",
        "text/plain",
        "text/markdown",
        "application/json",
        "text/csv",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ]
    
    # Allowed code formats
    ALLOWED_CODE_FORMATS = [
        "text/x-python",
        "text/javascript",
        "text/x-java-source",
        "text/x-c",
        "text/x-c++src",
        "text/x-go",
        "text/x-rust",
        "text/x-typescript",
        "text/html",
        "text/css",
        "application/json",
        "text/yaml",
        "text/xml",
    ]
    
    # File size limits (in bytes)
    MAX_IMAGE_SIZE = 10 * 1024 * 1024      # 10 MB
    MAX_DOCUMENT_SIZE = 50 * 1024 * 1024   # 50 MB
    MAX_CODE_SIZE = 1 * 1024 * 1024        # 1 MB
    MAX_AUDIO_SIZE = 100 * 1024 * 1024     # 100 MB
    MAX_VIDEO_SIZE = 500 * 1024 * 1024     # 500 MB
    
    # File name constraints
    MAX_FILENAME_LENGTH = 255
    MIN_FILENAME_LENGTH = 1
    
    # Storage providers
    STORAGE_LOCAL = "local"
    STORAGE_SUPABASE = "supabase"
    STORAGE_AWS_S3 = "aws_s3"
    STORAGE_GOOGLE_CLOUD = "google_cloud"
    
    VALID_STORAGE_PROVIDERS = [
        STORAGE_LOCAL,
        STORAGE_SUPABASE,
        STORAGE_AWS_S3,
        STORAGE_GOOGLE_CLOUD,
    ]


# Timeline Constants
class TimelineConstants:
    """Timeline-related constants."""
    
    # Post types
    TYPE_TEXT = "text"
    TYPE_IMAGE = "image"
    TYPE_LINK = "link"
    TYPE_ACHIEVEMENT = "achievement"
    TYPE_SYSTEM = "system"
    
    VALID_POST_TYPES = [TYPE_TEXT, TYPE_IMAGE, TYPE_LINK, TYPE_ACHIEVEMENT, TYPE_SYSTEM]
    
    # Visibility levels
    VISIBILITY_PUBLIC = "public"
    VISIBILITY_FOLLOWERS = "followers"
    VISIBILITY_PRIVATE = "private"
    
    VALID_VISIBILITY_LEVELS = [VISIBILITY_PUBLIC, VISIBILITY_FOLLOWERS, VISIBILITY_PRIVATE]
    
    # Content constraints
    MAX_POST_CONTENT_LENGTH = 2000
    MAX_COMMENT_CONTENT_LENGTH = 500
    MAX_TAGS = 10
    MAX_TAG_LENGTH = 50


# Search Constants
class SearchConstants:
    """Search-related constants."""
    
    # Search types
    TYPE_USERS = "users"
    TYPE_AGENTS = "agents"
    TYPE_CONVERSATIONS = "conversations"
    TYPE_MESSAGES = "messages"
    TYPE_FILES = "files"
    TYPE_TIMELINE = "timeline"
    
    VALID_SEARCH_TYPES = [
        TYPE_USERS,
        TYPE_AGENTS,
        TYPE_CONVERSATIONS,
        TYPE_MESSAGES,
        TYPE_FILES,
        TYPE_TIMELINE,
    ]
    
    # Search constraints
    MIN_QUERY_LENGTH = 2
    MAX_QUERY_LENGTH = 200
    MAX_SEARCH_RESULTS = 100


# Security Constants
class SecurityConstants:
    """Security-related constants."""
    
    # JWT
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = 30
    
    # Password hashing
    BCRYPT_ROUNDS = 12
    
    # Session management
    SESSION_TIMEOUT_MINUTES = 30
    MAX_CONCURRENT_SESSIONS = 5
    
    # Rate limiting
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_LOCKOUT_MINUTES = 15
    
    # API keys
    API_KEY_LENGTH = 32
    API_KEY_PREFIX = "ca_"  # Connet AI


# Cache Constants
class CacheConstants:
    """Cache-related constants."""
    
    # Cache prefixes
    USER_PREFIX = "user"
    AGENT_PREFIX = "agent"
    CONVERSATION_PREFIX = "conversation"
    MESSAGE_PREFIX = "message"
    FILE_PREFIX = "file"
    SEARCH_PREFIX = "search"
    
    # Default TTL values (seconds)
    SHORT_TTL = 300     # 5 minutes
    MEDIUM_TTL = 1800   # 30 minutes
    LONG_TTL = 3600     # 1 hour
    VERY_LONG_TTL = 86400  # 24 hours


# Email Constants
class EmailConstants:
    """Email-related constants."""
    
    # Email types
    TYPE_WELCOME = "welcome"
    TYPE_VERIFICATION = "verification"
    TYPE_PASSWORD_RESET = "password_reset"
    TYPE_INVITATION = "invitation"
    TYPE_NOTIFICATION = "notification"
    
    # Email templates
    TEMPLATE_WELCOME = "welcome.html"
    TEMPLATE_VERIFICATION = "email_verification.html"
    TEMPLATE_PASSWORD_RESET = "password_reset.html"
    TEMPLATE_INVITATION = "invitation.html"


# Status Codes
class StatusCodes:
    """HTTP status codes."""
    
    # Success
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    
    # Client errors
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429
    
    # Server errors
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503


# Error Codes
class ErrorCodes:
    """Application error codes."""
    
    # Generic errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    
    # Auth errors
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    USER_NOT_VERIFIED = "USER_NOT_VERIFIED"
    USER_SUSPENDED = "USER_SUSPENDED"
    
    # User errors
    USER_EXISTS = "USER_EXISTS"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USERNAME_TAKEN = "USERNAME_TAKEN"
    EMAIL_TAKEN = "EMAIL_TAKEN"
    
    # Agent errors
    AGENT_NOT_FOUND = "AGENT_NOT_FOUND"
    AGENT_INACTIVE = "AGENT_INACTIVE"
    AGENT_NAME_TAKEN = "AGENT_NAME_TAKEN"
    
    # Conversation errors
    CONVERSATION_NOT_FOUND = "CONVERSATION_NOT_FOUND"
    NOT_CONVERSATION_PARTICIPANT = "NOT_CONVERSATION_PARTICIPANT"
    CONVERSATION_ARCHIVED = "CONVERSATION_ARCHIVED"
    
    # File errors
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    FILE_TYPE_NOT_ALLOWED = "FILE_TYPE_NOT_ALLOWED"
    UPLOAD_FAILED = "UPLOAD_FAILED"
    
    # Rate limiting
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"


# Environment Constants
class Environment:
    """Environment constants."""
    
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    
    VALID_ENVIRONMENTS = [DEVELOPMENT, TESTING, STAGING, PRODUCTION]