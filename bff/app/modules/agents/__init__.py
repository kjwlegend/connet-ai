"""Deprecated agents module. Re-exported from app.modules.ai.agents."""

from app.modules.ai.agents import *  # noqa: F401,F403

__all__ = [name for name in globals() if not name.startswith("_")]
