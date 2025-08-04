"""
Helper Utilities

This module provides general helper functions used across the application.
"""

import hashlib
import secrets
import string
import uuid
import re
from typing import Any, Dict, List, Optional, Union, Tuple
from urllib.parse import urlparse, parse_qs
import json
import base64

from app.utils.logging import get_logger

logger = get_logger(__name__)


class StringUtils:
    """String manipulation utilities."""
    
    @staticmethod
    def generate_random_string(
        length: int = 32,
        include_upper: bool = True,
        include_lower: bool = True,
        include_digits: bool = True,
        include_special: bool = False
    ) -> str:
        """Generate a random string with specified characteristics."""
        characters = ""
        
        if include_lower:
            characters += string.ascii_lowercase
        if include_upper:
            characters += string.ascii_uppercase
        if include_digits:
            characters += string.digits
        if include_special:
            characters += "!@#$%^&*"
        
        if not characters:
            characters = string.ascii_letters + string.digits
        
        return ''.join(secrets.choice(characters) for _ in range(length))
    
    @staticmethod
    def generate_uuid() -> str:
        """Generate a UUID string."""
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_short_id(length: int = 8) -> str:
        """Generate a short alphanumeric ID."""
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))
    
    @staticmethod
    def slugify(text: str, max_length: Optional[int] = None) -> str:
        """Convert text to URL-friendly slug."""
        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[\s_-]+', '-', slug)
        slug = slug.strip('-')
        
        if max_length:
            slug = slug[:max_length].rstrip('-')
        
        return slug
    
    @staticmethod
    def truncate_text(
        text: str,
        max_length: int,
        suffix: str = "..."
    ) -> str:
        """Truncate text to specified length with suffix."""
        if len(text) <= max_length:
            return text
        
        truncated_length = max_length - len(suffix)
        return text[:truncated_length] + suffix
    
    @staticmethod
    def clean_whitespace(text: str) -> str:
        """Clean excessive whitespace from text."""
        # Replace multiple whitespace with single space
        cleaned = re.sub(r'\s+', ' ', text)
        return cleaned.strip()
    
    @staticmethod
    def extract_mentions(text: str) -> List[str]:
        """Extract @mentions from text."""
        mention_pattern = r'@(\w+)'
        mentions = re.findall(mention_pattern, text)
        return list(set(mentions))  # Remove duplicates
    
    @staticmethod
    def extract_hashtags(text: str) -> List[str]:
        """Extract #hashtags from text."""
        hashtag_pattern = r'#(\w+)'
        hashtags = re.findall(hashtag_pattern, text)
        return list(set(hashtags))  # Remove duplicates
    
    @staticmethod
    def mask_email(email: str) -> str:
        """Mask email address for privacy."""
        if '@' not in email:
            return email
        
        local, domain = email.split('@', 1)
        if len(local) <= 2:
            masked_local = '*' * len(local)
        else:
            masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
        
        return f"{masked_local}@{domain}"
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format."""
        # Username should be 3-50 chars, alphanumeric + underscore, no consecutive underscores
        if not (3 <= len(username) <= 50):
            return False
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False
        
        if '__' in username or username.startswith('_') or username.endswith('_'):
            return False
        
        return True


class HashUtils:
    """Hashing utilities."""
    
    @staticmethod
    def hash_string(text: str, algorithm: str = 'sha256') -> str:
        """Hash a string using specified algorithm."""
        if algorithm == 'md5':
            return hashlib.md5(text.encode()).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(text.encode()).hexdigest()
        elif algorithm == 'sha256':
            return hashlib.sha256(text.encode()).hexdigest()
        elif algorithm == 'sha512':
            return hashlib.sha512(text.encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    @staticmethod
    def hash_file_content(content: bytes, algorithm: str = 'sha256') -> str:
        """Hash file content."""
        if algorithm == 'md5':
            return hashlib.md5(content).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(content).hexdigest()
        elif algorithm == 'sha256':
            return hashlib.sha256(content).hexdigest()
        elif algorithm == 'sha512':
            return hashlib.sha512(content).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    @staticmethod
    def generate_hash_key(*args) -> str:
        """Generate a hash key from multiple arguments."""
        combined = ':'.join(str(arg) for arg in args)
        return HashUtils.hash_string(combined)


class DataUtils:
    """Data manipulation utilities."""
    
    @staticmethod
    def safe_get(data: dict, key: str, default: Any = None) -> Any:
        """Safely get value from dictionary."""
        return data.get(key, default)
    
    @staticmethod
    def deep_get(data: dict, key_path: str, default: Any = None) -> Any:
        """Get value from nested dictionary using dot notation."""
        keys = key_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current
    
    @staticmethod
    def flatten_dict(data: dict, separator: str = '.') -> dict:
        """Flatten nested dictionary."""
        def _flatten(obj, parent_key=''):
            items = []
            for key, value in obj.items():
                new_key = f"{parent_key}{separator}{key}" if parent_key else key
                
                if isinstance(value, dict):
                    items.extend(_flatten(value, new_key).items())
                else:
                    items.append((new_key, value))
            return dict(items)
        
        return _flatten(data)
    
    @staticmethod
    def chunk_list(data: list, chunk_size: int) -> List[list]:
        """Split list into chunks of specified size."""
        return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    
    @staticmethod
    def remove_none_values(data: dict) -> dict:
        """Remove None values from dictionary."""
        return {k: v for k, v in data.items() if v is not None}
    
    @staticmethod
    def merge_dicts(*dicts) -> dict:
        """Merge multiple dictionaries."""
        result = {}
        for d in dicts:
            if isinstance(d, dict):
                result.update(d)
        return result


class FileUtils:
    """File-related utilities."""
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Get file extension from filename."""
        return filename.split('.')[-1].lower() if '.' in filename else ''
    
    @staticmethod
    def get_content_type_from_extension(extension: str) -> str:
        """Get MIME type from file extension."""
        content_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'svg': 'image/svg+xml',
            'pdf': 'application/pdf',
            'txt': 'text/plain',
            'md': 'text/markdown',
            'json': 'application/json',
            'csv': 'text/csv',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'py': 'text/x-python',
            'js': 'text/javascript',
            'ts': 'text/x-typescript',
            'html': 'text/html',
            'css': 'text/css',
            'xml': 'text/xml',
            'yaml': 'text/yaml',
            'yml': 'text/yaml',
        }
        return content_types.get(extension.lower(), 'application/octet-stream')
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage."""
        # Remove or replace unsafe characters
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove leading/trailing dots and spaces
        safe_filename = safe_filename.strip('. ')
        # Ensure it's not empty
        if not safe_filename:
            safe_filename = 'unnamed_file'
        
        return safe_filename
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"


class URLUtils:
    """URL manipulation utilities."""
    
    @staticmethod
    def parse_url(url: str) -> dict:
        """Parse URL into components."""
        parsed = urlparse(url)
        return {
            'scheme': parsed.scheme,
            'netloc': parsed.netloc,
            'path': parsed.path,
            'params': parsed.params,
            'query': dict(parse_qs(parsed.query)),
            'fragment': parsed.fragment
        }
    
    @staticmethod
    def extract_utm_params(url: str) -> dict:
        """Extract UTM parameters from URL."""
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        utm_params = {}
        for key, value in query_params.items():
            if key.startswith('utm_'):
                utm_params[key] = value[0] if value else None
        
        return utm_params
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False


class JSONUtils:
    """JSON utilities."""
    
    @staticmethod
    def safe_json_loads(json_str: str, default: Any = None) -> Any:
        """Safely parse JSON string."""
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError):
            return default
    
    @staticmethod
    def safe_json_dumps(obj: Any, default: str = "null") -> str:
        """Safely serialize object to JSON."""
        try:
            return json.dumps(obj, default=str, ensure_ascii=False)
        except (TypeError, ValueError):
            return default
    
    @staticmethod
    def pretty_json(obj: Any) -> str:
        """Format object as pretty JSON."""
        try:
            return json.dumps(obj, indent=2, default=str, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(obj)


class EncodingUtils:
    """Encoding/decoding utilities."""
    
    @staticmethod
    def base64_encode(data: Union[str, bytes]) -> str:
        """Encode data to base64."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return base64.b64encode(data).decode('utf-8')
    
    @staticmethod
    def base64_decode(encoded_data: str) -> bytes:
        """Decode base64 data."""
        return base64.b64decode(encoded_data)
    
    @staticmethod
    def url_safe_base64_encode(data: Union[str, bytes]) -> str:
        """Encode data to URL-safe base64."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')
    
    @staticmethod
    def url_safe_base64_decode(encoded_data: str) -> bytes:
        """Decode URL-safe base64 data."""
        # Add padding if needed
        padding = 4 - len(encoded_data) % 4
        if padding != 4:
            encoded_data += '=' * padding
        return base64.urlsafe_b64decode(encoded_data)


class ValidationUtils:
    """Validation utilities."""
    
    @staticmethod
    def is_valid_uuid(uuid_string: str) -> bool:
        """Check if string is a valid UUID."""
        try:
            uuid.UUID(uuid_string)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
        """Validate password strength and return issues."""
        issues = []
        
        if len(password) < 8:
            issues.append("Password must be at least 8 characters long")
        
        if not re.search(r'[a-z]', password):
            issues.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'[A-Z]', password):
            issues.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'\d', password):
            issues.append("Password must contain at least one digit")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            issues.append("Password must contain at least one special character")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
        """Sanitize user input."""
        # Strip whitespace
        sanitized = text.strip()
        
        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')
        
        # Limit length if specified
        if max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized