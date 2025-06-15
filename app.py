"""Compatibility shim for legacy `import app` references.

The real Flask application now lives in `backend.app`.
This shim re-exports symbols so other scripts keep working while we
transition.
"""
import importlib, sys

_real = importlib.import_module('backend.app')

# Re-export common names
for _name in ['app', 'db', 'initialize_database']:
    if hasattr(_real, _name):
        globals()[_name] = getattr(_real, _name)

# Also make submodules accessible via sys.modules
sys.modules[__name__] = _real
