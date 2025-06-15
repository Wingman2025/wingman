"""WSGI entrypoint for Gunicorn/Production.

Usage in Procfile:
    web: flask db upgrade && gunicorn -w 4 -b 0.0.0.0:$PORT backend.wsgi:application
"""

# Ensure project root in sys.path
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import the application factory from the backend package
from .app_factory import create_app


application = create_app()
