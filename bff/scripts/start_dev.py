
"""Start the BFF service with environment-aware configuration."""

import os
import sys
from pathlib import Path
from typing import Literal, Tuple

import uvicorn

# Ensure the app directory is on the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.settings import get_settings


EnvironmentKey = Literal["local", "uat", "prod"]

BASE_DIR = Path(__file__).resolve().parent.parent

ENVIRONMENT_PROFILES = {
    "local": {
        "env_file": ".env.local",
        "label": "Local Development",
    },
    "uat": {
        "env_file": ".env.uat",
        "label": "User Acceptance Testing",
    },
    "prod": {
        "env_file": ".env.prod",
        "label": "Production",
    },
}


def configure_environment(environment: EnvironmentKey) -> Tuple[dict, Path]:
    """Select the environment profile and export its env file location."""
    profile = ENVIRONMENT_PROFILES.get(environment)
    if profile is None:
        raise ValueError(f"Unknown environment '{environment}'.")

    env_path = (BASE_DIR / profile["env_file"]).resolve()
    if not env_path.exists():
        raise FileNotFoundError(
            f"Environment file '{env_path}' was not found. Create it before starting the server."
        )

    os.environ["BFF_ENV_FILE"] = str(env_path)
    os.environ["BFF_ENV"] = environment
    return profile, env_path


def start(environment: EnvironmentKey = "local") -> None:
    """Boot the FastAPI application for the requested environment."""
    profile, env_path = configure_environment(environment)
    settings = get_settings()

    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print(f"📍 Environment: {profile['label']} ({settings.app_env})")
    print(f"🗂  Env file: {env_path}")
    print(f"🌐 Server: http://{settings.host}:{settings.port}")
    print(f"📚 API Docs: http://{settings.host}:{settings.port}/docs")
    print("=" * 50)

    uvicorn.run(
        "app.main:create_app",
        factory=True,
        host=settings.host,
        port=settings.port,
        reload=settings.reload and settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True,
    )


def main() -> None:
    """Start the service using the local development profile."""
    start("local")


if __name__ == "__main__":
    main()
