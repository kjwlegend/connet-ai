"""
Environment Setup Script

This script helps create a .env file from the template.
"""

import os
import secrets
from pathlib import Path


def generate_secret_key() -> str:
    """Generate a secure secret key."""
    return secrets.token_urlsafe(32)


def create_env_file():
    """Create .env file from template."""
    project_root = Path(__file__).parent.parent
    env_example_path = project_root / ".env.example"
    env_path = project_root / ".env"

    if env_path.exists():
        print(f"⚠️  .env file already exists at {env_path}")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("❌ Aborted")
            return

    if not env_example_path.exists():
        print(f"❌ .env.example file not found at {env_example_path}")
        return

    with open(env_example_path, 'r') as f:
        content = f.read()

    secret_key = generate_secret_key()
    content = content.replace('SECRET_KEY=""', f'SECRET_KEY="{secret_key}"')

    with open(env_path, 'w') as f:
        f.write(content)

    print(f"✅ Created .env file at {env_path}")
    print("📝 Please edit the .env file and configure the following:")
    print("   - SUPABASE_URL")
    print("   - SUPABASE_ANON_KEY")
    print("   - SUPABASE_SERVICE_ROLE_KEY")
    print("   - DATABASE_URL")
    print("   - OPENAI_API_KEY")
    print("   - REDIS_URL (if using external Redis)")


def main():
    """Main function."""
    print("🔧 Connet.AI BFF Environment Setup")
    print("=" * 40)
    create_env_file()


if __name__ == "__main__":
    main()
