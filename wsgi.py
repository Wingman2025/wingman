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
        try:
            from railway_init import init_railway_db
            init_railway_db()
            print("Inicialización de Railway completada con éxito")
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

# Verificar que las tablas existen después de la inicialización
with application.app_context():
    from app import get_db
    db = get_db()
    try:
        # Verificar tabla skill
        result = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='skill'").fetchone()
        if result:
            print("Tabla 'skill' existe en la base de datos")
            # Contar habilidades
            count = db.execute("SELECT COUNT(*) FROM skill").fetchone()[0]
            print(f"Número de habilidades en la base de datos: {count}")
        else:
            print("ADVERTENCIA: La tabla 'skill' NO existe en la base de datos")
            # Intentar crear la tabla skill de emergencia
            print("Intentando crear tabla 'skill' de emergencia...")
            from railway_init import init_railway_db
            init_railway_db()
    except Exception as e:
        print(f"Error al verificar tablas: {e}")

# PythonAnywhere looks for an 'application' object by default
if __name__ == '__main__':
    application.run(debug=False)
