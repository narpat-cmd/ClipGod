"""ClipGod Application Package"""
__version__ = "1.0.0"

from .core.config import settings
from .db.session import init_db

__all__ = ["settings", "init_db"]