"""Compatibility shim.

This temporary file keeps legacy imports `import models` working after the
actual models were moved to `backend/models/legacy.py`.
Remove after all modules are updated to use `from backend.models import ...`.
"""
import importlib, sys

sys.modules[__name__] = importlib.import_module('backend.models.legacy')
