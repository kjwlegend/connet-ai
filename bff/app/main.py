"""
FastAPI Application Entry Point

This module contains the main FastAPI application factory and startup/shutdown logic.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.middleware import (
    PerformanceMonitoringMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
)
from app.api.v1.router import api_router
from app.config.settings import get_settings
from app.infrastructure.cache.redis_client import get_redis_client
from app.infrastructure.database.connection import init_database
from app.infrastructure.external.supabase.client import init_supabase
from app.infrastructure.messaging.event_bus import get_event_bus
from app.utils.logging import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    settings = get_settings()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    try:
        # Initialize core services
        await init_database()
        
        # Try to connect to Redis (optional for development)
        try:
            redis_client = await get_redis_client()
            await redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed (continuing without cache): {e}")
        
        await init_supabase()
        
        # Initialize event bus
        event_bus = get_event_bus()
        await event_bus.start()
        
        logger.info("All services initialized successfully")
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    finally:
        # Cleanup
        logger.info("Shutting down services...")
        
        # Close event bus
        event_bus = get_event_bus()
        await event_bus.stop()
        
        # Close Redis connection (if available)
        try:
            redis_client = await get_redis_client()
            await redis_client.close()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.warning(f"Error closing Redis connection: {e}")
        
        logger.info("Shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    # Setup logging
    setup_logging(settings.log_level, settings.app_env)
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        description="Backend for Frontend service for Connet.AI platform",
        version=settings.app_version,
        openapi_url="/api/v1/openapi.json" if settings.debug else None,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )
    
    # Add security middleware
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Add trusted host middleware
    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", "*.connet.ai"]
        )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )
    
    # Add rate limiting middleware
    app.add_middleware(RateLimitMiddleware)
    
    # Add performance monitoring middleware
    app.add_middleware(PerformanceMonitoringMiddleware)
    
    # Include API router
    app.include_router(api_router, prefix="/api/v1")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.app_version,
            "environment": settings.app_env
        }
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": settings.app_version,
            "docs": "/docs" if settings.debug else None
        }
    
    return app


# Create app instance for direct import (for uvicorn app.main:app)
app = create_app()


def run_dev():
    """Run development server."""
    settings = get_settings()
    uvicorn.run(
        "app.main:create_app",
        factory=True,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )


def run_prod():
    """Run production server."""
    settings = get_settings()
    uvicorn.run(
        "app.main:create_app",
        factory=True,
        host=settings.host,
        port=settings.port,
        workers=4,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    run_dev()