"""
API Middleware

This module contains custom middleware for the FastAPI application.
"""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config.settings import get_settings
from app.infrastructure.cache.redis_client import get_redis_client
from app.utils.logging import get_logger

logger = get_logger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to all responses."""
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # HSTS for HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Monitor API performance and log metrics."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Monitor request performance."""
        start_time = time.time()
        
        # Extract request info
        method = request.method
        path = request.url.path
        user_agent = request.headers.get("user-agent", "")
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log performance metrics
            logger.info(
                "API request completed",
                extra={
                    "method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "user_agent": user_agent,
                }
            )
            
            # Add performance headers
            response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
            
            return response
            
        except Exception as e:
            # Calculate error duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error
            logger.error(
                "API request failed",
                extra={
                    "method": method,
                    "path": path,
                    "duration_ms": duration_ms,
                    "error": str(e),
                    "user_agent": user_agent,
                }
            )
            
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis."""
    
    def __init__(self, app, calls_per_minute: int = 60, burst_limit: int = 10):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self.burst_limit = burst_limit
        self.window_size = 60  # 1 minute in seconds
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Apply rate limiting."""
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)
        
        # Get client identifier
        client_id = self._get_client_identifier(request)
        
        # Check rate limit
        if not await self._is_request_allowed(client_id):
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.calls_per_minute} requests per minute allowed",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        return await call_next(request)
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Try to get user ID from JWT token first
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                # In a real implementation, we'd decode the JWT here
                # For now, use the token as identifier
                return f"user:{auth_header}"
            except:
                pass
        
        # Fall back to IP address
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Get the first IP in the chain
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        return f"ip:{client_ip}"
    
    async def _is_request_allowed(self, client_id: str) -> bool:
        """Check if request is allowed based on rate limits."""
        try:
            redis_client = await get_redis_client()
            current_time = int(time.time())
            window_start = current_time - self.window_size
            
            # Use sliding window rate limiting
            key = f"rate_limit:{client_id}"
            
            # Remove old entries
            await redis_client.zremrangebyscore(key, 0, window_start)
            
            # Count current requests in window
            current_count = await redis_client.zcard(key)
            
            # Check if under limit
            if current_count >= self.calls_per_minute:
                return False
            
            # Add current request
            await redis_client.zadd(key, {str(current_time): current_time})
            
            # Set expiration for cleanup
            await redis_client.expire(key, self.window_size * 2)
            
            return True
            
        except Exception as e:
            logger.warning(f"Rate limiting error: {e}")
            # Allow request if rate limiting fails
            return True


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all incoming requests."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request details."""
        # Extract request info
        method = request.method
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else None
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")
        
        # Log request
        logger.info(
            "Incoming request",
            extra={
                "method": method,
                "path": path,
                "query_params": query_params,
                "client_ip": client_ip,
                "user_agent": user_agent,
            }
        )
        
        return await call_next(request)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle uncaught exceptions."""
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(
                "Unhandled exception",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                exc_info=True
            )
            
            # Return generic error response
            settings = get_settings()
            if settings.debug:
                # In debug mode, return detailed error
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": "Internal server error",
                        "detail": str(e),
                        "type": type(e).__name__,
                    }
                )
            else:
                # In production, return generic error
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": "Internal server error",
                        "message": "An unexpected error occurred",
                    }
                )