"""
Generate Alembic migration script

This standalone script generates database migrations.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Generate migration using alembic command line."""
    try:
        # Set minimal environment
        os.environ.setdefault('APP_ENV', 'development')
        os.environ.setdefault('DEBUG', 'true')
        
        # Import and run alembic
        from alembic.config import Config
        from alembic import command
        
        # Create alembic config
        alembic_cfg = Config('alembic.ini')
        
        # Generate migration
        command.revision(
            alembic_cfg,
            autogenerate=True,
            message="Initial database schema with all models"
        )
        
        print("✅ Migration generated successfully!")
        
    except Exception as e:
        print(f"❌ Error generating migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()