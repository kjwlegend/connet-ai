"""Application lifespan management."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.config.settings import get_settings
from app.core.cache import get_redis_client
from app.core.db import init_database
from app.infrastructure.external.supabase.client import init_supabase
from app.infrastructure.messaging.event_bus import get_event_bus

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """FastAPI lifespan context manager."""
    settings = get_settings()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    event_bus = get_event_bus()
    redis_client = None

    try:
        await init_database()

        try:
            redis_client = await get_redis_client()
            await redis_client.ping()
            logger.info("Redis connection established")
        except Exception as exc:  # pragma: no cover - optional dependency
            logger.warning(
                "Redis connection failed (continuing without cache): %s", exc
            )

        await init_supabase()

        await event_bus.start()

        logger.info("All services initialized successfully")
        yield

    except Exception as exc:
        logger.error("Failed to initialize services: %s", exc)
        raise
    finally:
        logger.info("Shutting down services...")

        try:
            await event_bus.stop()
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to stop event bus cleanly: %s", exc)

        if redis_client:
            try:
                await redis_client.close()
                logger.info("Redis connection closed")
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("Error closing Redis connection: %s", exc)

        logger.info("Shutdown complete")


__all__ = ["lifespan"]
