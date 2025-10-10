#!/usr/bin/env python3
"""
Authentication Setup Script

This script helps set up the authentication system by:
1. Validating environment variables
2. Testing Supabase connection
3. Creating database schema
4. Setting up initial data
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from app.config.settings import get_settings
from app.infrastructure.external.supabase.client import get_supabase_client
from app.services.supabase_auth_service import SupabaseAuthService
from app.utils.logging import get_logger

logger = get_logger(__name__)


def validate_environment():
    """Validate required environment variables."""
    settings = get_settings()
    
    required_vars = [
        ("SUPABASE_URL", settings.supabase_url),
        ("SUPABASE_ANON_KEY", settings.supabase_anon_key),
        ("SUPABASE_SERVICE_ROLE_KEY", settings.supabase_service_role_key),
        ("DATABASE_URL", settings.database_url),
        ("SECRET_KEY", settings.secret_key),
    ]
    
    missing_vars = []
    
    for var_name, var_value in required_vars:
        if not var_value or var_value == "":
            missing_vars.append(var_name)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.info("Please check your .env file and ensure all required variables are set.")
        return False
    
    logger.info("All required environment variables are set ✓")
    return True


async def test_supabase_connection():
    """Test connection to Supabase."""
    try:
        client = get_supabase_client()
        
        # Test basic connection by checking auth status
        response = client.auth.get_session()
        logger.info("Supabase connection test successful ✓")
        
        return True
        
    except Exception as e:
        logger.error(f"Supabase connection test failed: {e}")
        return False


async def test_database_connection():
    """Test connection to PostgreSQL database."""
    try:
        from sqlalchemy import text
        from app.core.db import create_engine
        settings = get_settings()
        
        engine = create_engine(settings.database_url)
        
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.scalar()
            
        await engine.dispose()
        
        logger.info("Database connection test successful ✓")
        return True
        
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


async def setup_database_schema():
    """Set up database schema."""
    try:
        from scripts.init_database import create_tables, create_initial_data
        
        logger.info("Setting up database schema...")
        await create_tables()
        
        logger.info("Creating initial data...")
        await create_initial_data()
        
        logger.info("Database schema setup completed ✓")
        return True
        
    except Exception as e:
        logger.error(f"Database schema setup failed: {e}")
        return False


async def test_auth_flow():
    """Test the authentication flow."""
    try:
        from app.api.dependencies import get_user_repository
        from app.core.db import get_session
        
        # This is a basic test to ensure our auth service can be instantiated
        async with get_session() as session:
            user_repo = await get_user_repository(session)
            auth_service = SupabaseAuthService(user_repository=user_repo)
            
            logger.info("Authentication service initialization test successful ✓")
            return True
            
    except Exception as e:
        logger.error(f"Authentication service test failed: {e}")
        return False


async def main():
    """Main setup function."""
    logger.info("🚀 Starting authentication setup...")
    
    # Step 1: Validate environment
    if not validate_environment():
        logger.error("❌ Environment validation failed")
        sys.exit(1)
    
    # Step 2: Test Supabase connection
    if not await test_supabase_connection():
        logger.error("❌ Supabase connection test failed")
        sys.exit(1)
    
    # Step 3: Test database connection
    if not await test_database_connection():
        logger.error("❌ Database connection test failed")
        sys.exit(1)
    
    # Step 4: Setup database schema
    setup_db = input("Do you want to set up the database schema? (y/N): ").lower().strip()
    if setup_db == 'y':
        if not await setup_database_schema():
            logger.error("❌ Database schema setup failed")
            sys.exit(1)
    
    # Step 5: Test auth flow
    if not await test_auth_flow():
        logger.error("❌ Authentication service test failed")
        sys.exit(1)
    
    logger.info("✅ Authentication setup completed successfully!")
    logger.info("\nNext steps:")
    logger.info("1. Start the BFF service: python -m uvicorn app.main:app --reload")
    logger.info("2. Test the API endpoints at http://localhost:8000/docs")
    logger.info("3. Register a new user via POST /api/v1/auth/register")
    logger.info("4. Login via POST /api/v1/auth/login")


if __name__ == "__main__":
    asyncio.run(main())
