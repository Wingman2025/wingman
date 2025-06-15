"""Temporary app factory that returns the legacy Flask instance.

This allows us to switch Gunicorn and any external callers to
`backend.app_factory:create_app` (via `backend.wsgi:application`) while we
incrementally refactor the real factory inside `backend/`.
"""
from importlib import import_module
from typing import Any

_app_cache: Any = None

def create_app():
    """Return the existing Flask app from the legacy root `app.py`."""
    global _app_cache
    if _app_cache is None:
        legacy_mod = import_module('app')
        _app_cache = getattr(legacy_mod, 'app')
    return _app_cache
