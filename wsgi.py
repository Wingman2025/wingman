import sys
import os

# Add the project directory to the Python path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

# Import the Flask app and initialization function
from app import app as application, initialize_database

# Detectar si estamos en Railway (Railway establece la variable de entorno RAILWAY_ENVIRONMENT)
is_railway = os.environ.get('RAILWAY_ENVIRONMENT') is not None

# Inicializar la base de datos según el entorno
with application.app_context():
    if is_railway:
        # Si estamos en Railway, usar el script específico de Railway
        print("Detectado entorno Railway, usando inicialización específica...")
        from railway_init import init_railway_db
        init_railway_db()
    else:
        # En entorno local o PythonAnywhere, usar la inicialización estándar
        initialize_database()

# PythonAnywhere looks for an 'application' object by default
if __name__ == '__main__':
    application.run(debug=False)
