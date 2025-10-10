"""
FastAPI Application Entry Point

This module contains the main FastAPI application factory and startup/shutdown logic.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.lifespan import lifespan
from app.api.middleware import (
    PerformanceMonitoringMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
)
from app.api.routers import api
from app.config.settings import get_settings
from app.utils.logging import setup_logging


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
    
    # Include API router (versioned under /api)
    app.include_router(api, prefix="/api")
    
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
