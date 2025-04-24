import os
import sys
from app import app, initialize_database

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use the port assigned by Railway
    
    # Detectar si estamos en Railway
    is_railway = os.environ.get('RAILWAY_ENVIRONMENT') is not None
    
    # Inicializar la base de datos según el entorno
    with app.app_context():
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
            # En entorno local, usar la inicialización estándar
            initialize_database()
    
    app.run(debug=False, host='0.0.0.0', port=port)
