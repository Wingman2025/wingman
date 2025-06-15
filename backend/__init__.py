"""Backend package placeholder.

After running scripts/restructure_project.py, this package contendrá la
aplicación Flask como un factory (create_app) y submódulos (models, api, etc.).
Por ahora solo sirve para reservar la ruta.
"""

"""Backend package – transición a estructura modular.

Por ahora reutilizamos `app.app` existente para no romper nada.
Más adelante copiaremos la lógica a un factory completo.
"""

from importlib import import_module
from typing import Any

_flask_app_cache: Any = None

def create_app():
    """Return the Flask app instance from legacy `app.py`.

    Durante la fase de transición simplemente importa el módulo raíz `app`
    (antiguo), obtiene la variable `app` y la retorna. Esto permite que
    `backend.wsgi:application` funcione sin refactor inmediato.
    """
    global _flask_app_cache
    if _flask_app_cache is None:
        legacy_module = import_module('.app', package=__name__)  # app.py en la raíz
        _flask_app_cache = getattr(legacy_module, 'app')
    return _flask_app_cache

