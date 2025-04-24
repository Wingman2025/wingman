import sys
import os

# Add the project directory to the Python path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

# Import the Flask app and initialization function
from app import app as application, initialize_database
from railway_init import is_running_on_railway

# Detectar si estamos en Railway (Railway establece la variable de entorno RAILWAY_ENVIRONMENT)
is_railway = os.environ.get('RAILWAY_ENVIRONMENT') is not None

# Inicializar la base de datos según el entorno
with application.app_context():
    if is_railway:
        # Si estamos en Railway, usar el script específico de Railway
        print("Detectado entorno Railway, usando inicialización específica...")
        try:
            print("Detectado entorno Railway, usando inicialización específica...")
            with application.app_context():
                # Usar inicialización específica de Railway (si es necesario)
                initialize_database() # This handles migrations for PostgreSQL
        except Exception as e:
            print(f"Error durante la inicialización de Railway: {e}")
            print(f"Tipo de error: {type(e)}")
            print(f"Detalles del error: {sys.exc_info()}")
            # En caso de error, intentar con la inicialización estándar
            print("Intentando con inicialización estándar como respaldo...")
            initialize_database()
    else:
        # En entorno local o PythonAnywhere, usar la inicialización estándar
        initialize_database()

# PythonAnywhere looks for an 'application' object by default
if __name__ == '__main__':
    application.run(debug=False)
