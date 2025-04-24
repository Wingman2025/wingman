import os
import sys
from app import app, db, initialize_database
from railway_init import is_running_on_railway

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use the port assigned by Railway
    
    # Detectar si estamos en Railway
    is_railway = is_running_on_railway()
    
    # Inicializar la base de datos según el entorno
    with app.app_context():
        if is_railway:
            # Si estamos en Railway, usar el script específico de Railway
            print("Detectado entorno Railway, usando inicialización específica...")
            # Rely on standard Flask-Migrate initialization for all environments
            initialize_database()
        else:
            # En entorno local, usar la inicialización estándar
            initialize_database()
    
    app.run(debug=False, host='0.0.0.0', port=port)
