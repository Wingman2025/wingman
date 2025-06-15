"""Proxy blueprint that re-exports the existing `companion_bp` from the
legacy `companion_api.py` module.

This keeps imports consistent while we later migrate the real code here.
"""

from importlib import import_module as _import_module

_legacy = _import_module('companion_api')
companion_bp = getattr(_legacy, 'companion_bp')

__all__ = ['companion_bp']
