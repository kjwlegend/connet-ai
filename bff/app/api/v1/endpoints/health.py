"""
Health Check Endpoints

This module contains health check and status endpoints.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config.settings import Settings, get_settings
from app.infrastructure.cache.redis_client import get_redis_client
from app.infrastructure.database.connection import get_session
from app.infrastructure.external.supabase.client import get_supabase_client
from app.schemas.responses import HealthResponse
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check(
    settings: Settings = Depends(get_settings),
) -> HealthResponse:
    """Basic health check endpoint."""
    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
        timestamp=datetime.utcnow(),
    )


@router.get("/detailed")
async def detailed_health_check(
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """Detailed health check with service dependencies."""
    
    health_status = {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {},
    }
    
    all_healthy = True
    
    # Check database connection
    try:
        await session.execute("SELECT 1")
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        all_healthy = False
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
        logger.error(f"Database health check failed: {e}")
    
    # Check Redis connection
    try:
        redis_client = get_redis_client()
        await redis_client.ping()
        health_status["checks"]["redis"] = {
            "status": "healthy",
            "message": "Redis connection successful"
        }
    except Exception as e:
        all_healthy = False
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "message": f"Redis connection failed: {str(e)}"
        }
        logger.error(f"Redis health check failed: {e}")
    
    # Check Supabase connection
    try:
        supabase_client = get_supabase_client()
        # Simple test - check if we can access the client
        if supabase_client:
            health_status["checks"]["supabase"] = {
                "status": "healthy",
                "message": "Supabase client available"
            }
        else:
            raise Exception("Supabase client not initialized")
    except Exception as e:
        all_healthy = False
        health_status["checks"]["supabase"] = {
            "status": "unhealthy",
            "message": f"Supabase check failed: {str(e)}"
        }
        logger.error(f"Supabase health check failed: {e}")
    
    # Update overall status
    health_status["status"] = "healthy" if all_healthy else "unhealthy"
    
    # Return 503 if any service is unhealthy
    if not all_healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_status
        )
    
    return health_status


@router.get("/readiness")
async def readiness_check(
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """Readiness check for Kubernetes deployment."""
    
    # Check if the application is ready to serve traffic
    # This is a simplified check - in production you might want to check:
    # - Database migrations are complete
    # - Required configuration is loaded
    # - External dependencies are reachable
    
    try:
        # Basic checks
        checks = []
        
        # Check if settings are loaded
        if settings.app_name and settings.app_version:
            checks.append("settings_loaded")
        
        # Check if we're not in a startup phase
        # (In a real app, you might have a startup flag)
        checks.append("startup_complete")
        
        return {
            "status": "ready",
            "service": settings.app_name,
            "version": settings.app_version,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks,
        }
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "not_ready",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )


@router.get("/liveness")
async def liveness_check() -> Dict[str, Any]:
    """Liveness check for Kubernetes deployment."""
    
    # This should be a very lightweight check
    # It should only fail if the application is completely broken
    # and needs to be restarted
    
    try:
        # Check if the event loop is running
        loop = asyncio.get_running_loop()
        if loop.is_running():
            return {
                "status": "alive",
                "timestamp": datetime.utcnow().isoformat(),
            }
        else:
            raise Exception("Event loop not running")
            
    except Exception as e:
        logger.critical(f"Liveness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "dead",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )