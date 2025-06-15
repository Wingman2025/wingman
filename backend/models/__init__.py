"""Proxy module to reutilizar modelos existentes durante la migración.

Permite hacer `from backend.models import User, GoalTemplate, ...` mientras
`models.py` sigue en la raíz. En una fase posterior moveremos las clases
físicamente aquí y borraremos el archivo legacy.
"""

from importlib import import_module as _import_module

_legacy_models = _import_module('models')

# Exportar todo lo público
for _name in dir(_legacy_models):
    if not _name.startswith('_'):
        globals()[_name] = getattr(_legacy_models, _name)

del _import_module, _legacy_models, _name
