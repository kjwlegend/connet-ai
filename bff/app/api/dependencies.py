"""Backward-compatible shim for API dependencies.

All dependencies have moved to `app.api.deps` under the new modules layout.
"""

from app.api.deps import *  # noqa: F401,F403

__all__ = [name for name in globals().keys() if not name.startswith("_")]
