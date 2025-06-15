"""WSGI entrypoint for Gunicorn/Production.

Usage in Procfile:
    web: flask db upgrade && gunicorn -w 4 -b 0.0.0.0:$PORT backend.wsgi:application
"""

from importlib import import_module

# Lazy import to avoid circular deps if create_app references others
create_app = getattr(import_module('backend.app_factory', package='backend'), 'create_app', None)
if create_app is None:
    # Fallback: direct import from backend (if __init__.py will implement create_app soon)
    from backend import create_app  # type: ignore

application = create_app()
