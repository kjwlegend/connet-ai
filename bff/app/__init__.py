"""
Connet.AI BFF Service

Backend for Frontend service providing APIs for the Connet.AI platform.
"""

__version__ = "0.1.0"
__author__ = "Connet.AI Team"
__email__ = "dev@connet.ai"

from .main import create_app

__all__ = ["create_app"]