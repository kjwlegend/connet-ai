#!/usr/bin/env python3
"""
Database import script for migrated agent data.

This script imports the migrated agent data from migrated_agents.json
into the database using the SQLModel AIAgentModel.
"""

import json
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from uuid import UUID
from typing import List, Dict, Any

# Add the bff directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent / "bff"))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, Session, select
from app.infrastructure.database.models.agent_model import AIAgentModel
from app.infrastructure.database.models.user_model import UserModel

# Database configuration - update these with your actual database settings
DATABASE_URL = (
    "postgresql://postgres:your_secure_password_here@localhost:5432/connet_ai"
)


def create_default_user(session: Session, user_id: str) -> bool:
    """Create a default user if it doesn't exist."""
    try:
        # Check if user already exists
        existing_user = session.get(UserModel, UUID(user_id))
        if existing_user:
            print(f"User {user_id} already exists")
            return True

        # Create default user
        default_user = UserModel(
            id=UUID(user_id),
            email="admin@example.com",
            username="admin",
            full_name="Default Admin User",
            is_active=True,
            is_verified=True,
            registration_source="migration",
        )

        session.add(default_user)
        session.commit()
        print(f"Created default user: {user_id}")
        return True

    except Exception as e:
        print(f"Error creating default user: {e}")
        session.rollback()
        return False


def import_agents(migrated_data: Dict[str, Any], session: Session) -> int:
    """Import migrated agents into the database."""
    agents_data = migrated_data.get("agents", [])
    migration_info = migrated_data.get("migration_info", {})
    default_user_id = migration_info.get("default_user_id")

    if not default_user_id:
        print("Error: No default_user_id found in migration data")
        return 0

    # Create default user if it doesn't exist
    if not create_default_user(session, default_user_id):
        print("Failed to create/verify default user")
        return 0

    imported_count = 0
    errors = []

    for i, agent_data in enumerate(agents_data):
        try:
            # Check if agent already exists by name
            existing_agent = session.exec(
                select(AIAgentModel).where(AIAgentModel.name == agent_data["name"])
            ).first()

            if existing_agent:
                print(f"Agent '{agent_data['name']}' already exists, skipping...")
                continue

            # Convert string dates to datetime objects
            created_at = datetime.fromisoformat(agent_data["created_at"])
            updated_at = datetime.fromisoformat(agent_data["updated_at"])

            # Create AIAgentModel instance
            agent = AIAgentModel(
                id=UUID(agent_data["id"]),
                name=agent_data["name"],
                display_name=agent_data["display_name"],
                description=agent_data["description"],
                introduction=agent_data["introduction"],
                agent_type=agent_data["agent_type"],
                version=agent_data["version"],
                status=agent_data["status"],
                is_public=agent_data["is_public"],
                is_active=agent_data["is_active"],
                avatar_url=agent_data["avatar_url"],
                avatar_style=agent_data["avatar_style"],
                conversation_style=agent_data["conversation_style"],
                system_prompt=agent_data["system_prompt"],
                personality_config=agent_data["personality_config"],
                model_preferences=agent_data["model_preferences"],
                capabilities=agent_data["capabilities"],
                required_permissions=agent_data["required_permissions"],
                tags=agent_data["tags"],
                category=agent_data["category"],
                usage_count=agent_data["usage_count"],
                follower_count=agent_data["follower_count"],
                agent_metadata=agent_data["agent_metadata"],
                description_embedding=agent_data["description_embedding"],
                capabilities_embedding=agent_data["capabilities_embedding"],
                created_by=UUID(agent_data["created_by"]),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                last_used_at=None,
            )

            session.add(agent)
            imported_count += 1

            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{len(agents_data)} agents...")

        except Exception as e:
            error_msg = (
                f"Error importing agent {agent_data.get('name', 'Unknown')}: {e}"
            )
            errors.append(error_msg)
            print(error_msg)
            continue

    # Commit all changes
    try:
        session.commit()
        print(f"Successfully imported {imported_count} agents")

        if errors:
            print(f"\nErrors encountered ({len(errors)}):")
            for error in errors:
                print(f"  - {error}")

    except Exception as e:
        session.rollback()
        print(f"Error committing to database: {e}")
        return 0

    return imported_count


def main():
    """Main import function."""
    input_file = Path("scripts/migrated_agents.json")

    if not input_file.exists():
        print(f"Error: Migrated data file not found: {input_file}")
        print("Please run the migration script first: python scripts/migrate_agents.py")
        return

    print("Agent Data Import Script")
    print("=" * 50)
    print(f"Loading migrated data from: {input_file}")

    # Load migrated data
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            migrated_data = json.load(f)
    except Exception as e:
        print(f"Error loading migrated data: {e}")
        return

    migration_info = migrated_data.get("migration_info", {})
    print(f"Migration date: {migration_info.get('migration_date')}")
    print(f"Total agents: {migration_info.get('total_agents')}")
    print(f"Migrated agents: {migration_info.get('migrated_agents')}")
    print(f"Default user ID: {migration_info.get('default_user_id')}")

    # Database setup
    print(f"\nConnecting to database...")
    print(f"Database URL: {DATABASE_URL}")
    print("Note: Please update DATABASE_URL with your actual database settings")

    # Confirm before proceeding
    confirm = input("\nProceed with import? (y/N): ").lower().strip()
    if confirm != "y":
        print("Import cancelled")
        return

    try:
        # Create engine and session
        engine = create_engine(DATABASE_URL, echo=False)

        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("Database connection successful")

        # Create tables if they don't exist
        SQLModel.metadata.create_all(engine)

        # Import agents
        with Session(engine) as session:
            imported_count = import_agents(migrated_data, session)

        print(f"\nImport completed successfully!")
        print(f"Imported agents: {imported_count}")

    except Exception as e:
        print(f"Database error: {e}")
        print("\nPlease check:")
        print("1. Database is running and accessible")
        print("2. DATABASE_URL is correct")
        print("3. User has proper database permissions")
        print("4. Required database tables exist")


if __name__ == "__main__":
    main()
