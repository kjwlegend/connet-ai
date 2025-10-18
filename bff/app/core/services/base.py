"""Shared base service definitions."""

from abc import ABC
from typing import Any, Callable, Dict, Optional

from app.core.cache import CacheManager
from app.utils.logging import get_logger


class BaseService(ABC):
    """Base service class with optional caching helpers."""

    def __init__(
        self,
        cache_manager: Optional[CacheManager] = None,
        logger_name: Optional[str] = None,
    ):
        self.cache_manager = cache_manager
        self.logger = get_logger(logger_name or self.__class__.__name__)

    async def _get_from_cache(self, key: str, default: Any = None) -> Any:
        if not self.cache_manager:
            return default

        try:
            return await self.cache_manager.get(key, default)
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.warning("Cache get failed for %s: %s", key, exc)
            return default

    async def _set_to_cache(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None,
    ) -> bool:
        if not self.cache_manager:
            return False

        try:
            await self.cache_manager.set(key, value, expire=expire)
            return True
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.warning("Cache set failed for %s: %s", key, exc)
            return False

    async def _delete_from_cache(self, key: str) -> bool:
        if not self.cache_manager:
            return False

        try:
            await self.cache_manager.delete(key)
            return True
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.warning("Cache delete failed for %s: %s", key, exc)
            return False

    async def _invalidate_cache_pattern(self, pattern: str) -> bool:
        if not self.cache_manager:
            return False

        try:
            await self.cache_manager.delete_pattern(pattern)
            return True
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.warning("Cache pattern invalidation failed for %s: %s", pattern, exc)
            return False

    def _log_info(self, message: str, **kwargs) -> None:
        if kwargs:
            message = f"{message} - Context: {kwargs}"
        self.logger.info(message)

    def _log_warning(self, message: str, **kwargs) -> None:
        if kwargs:
            message = f"{message} - Context: {kwargs}"
        self.logger.warning(message)

    def _log_error(
        self,
        message: str,
        exception: Optional[Exception] = None,
        **kwargs,
    ) -> None:
        if kwargs:
            message = f"{message} - Context: {kwargs}"

        if exception:
            self.logger.error("%s - Error: %s", message, exception)
        else:
            self.logger.error(message)

    def _validate_required_params(
        self,
        params: Dict[str, Any],
        required: list,
    ) -> None:
        missing = [
            param
            for param in required
            if param not in params or params[param] is None
        ]
        if missing:
            raise ValueError(f"Missing required parameters: {', '.join(missing)}")

    def _sanitize_string(
        self,
        value: str,
        max_length: Optional[int] = None,
    ) -> str:
        if not isinstance(value, str):
            raise ValueError("Value must be a string")

        sanitized = value.strip()
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        return sanitized

    def _format_error_response(
        self,
        error_code: str,
        message: str,
        details: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        response = {"error": {"code": error_code, "message": message}}
        if details:
            response["error"]["details"] = details
        return response

    def _format_success_response(
        self,
        data: Any,
        message: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        response = {"success": True, "data": data}
        if message:
            response["message"] = message
        if metadata:
            response["metadata"] = metadata
        return response


class BaseAsyncService(BaseService):
    """Base async service supporting context management."""

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False


class BaseRepositoryService(BaseService):
    """Base service class for repository-backed services."""

    def __init__(
        self,
        repository: Any,
        cache_manager: Optional[CacheManager] = None,
        logger_name: Optional[str] = None,
    ):
        super().__init__(cache_manager, logger_name)
        self.repository = repository

    async def _get_entity_by_id(
        self,
        entity_id: str,
        cache_key_generator: Optional[Callable[[str], str]] = None,
        cache_expire: Optional[int] = None,
    ):
        if cache_key_generator and self.cache_manager:
            cache_key = cache_key_generator(entity_id)
            cached_entity = await self._get_from_cache(cache_key)
            if cached_entity:
                return cached_entity

        entity = await self.repository.get_by_id(entity_id)

        if entity and cache_key_generator and self.cache_manager:
            cache_key = cache_key_generator(entity_id)
            await self._set_to_cache(cache_key, entity, expire=cache_expire)

        return entity

    async def _create_entity(
        self,
        entity_data: Any,
        invalidate_patterns: Optional[list] = None,
    ):
        entity = await self.repository.create(entity_data)

        if invalidate_patterns:
            for pattern in invalidate_patterns:
                await self._invalidate_cache_pattern(pattern)

        return entity

    async def _update_entity(
        self,
        entity_id: str,
        update_data: Dict,
        invalidate_patterns: Optional[list] = None,
    ):
        entity = await self.repository.update(entity_id, update_data)

        if invalidate_patterns:
            for pattern in invalidate_patterns:
                await self._invalidate_cache_pattern(pattern)

        return entity

    async def _delete_entity(
        self,
        entity_id: str,
        invalidate_patterns: Optional[list] = None,
    ) -> bool:
        success = await self.repository.delete(entity_id)

        if success and invalidate_patterns:
            for pattern in invalidate_patterns:
                await self._invalidate_cache_pattern(pattern)

        return success
