"""Proxy module for existing companion_api blueprint during migration.

Allows `from backend.api import companion_bp` or future registration loops.
"""

"""API package que expone blueprints del backend.

Durante la migración importamos blueprints desde módulos internos dentro
de `backend.api`. Actualmente sólo hay `companion_bp`.
"""

from .companion import companion_bp  # noqa: F401

__all__ = [
    'companion_bp',
]

