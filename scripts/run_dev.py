import os
from pathlib import Path
import sys
# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app import app, db, initialize_database

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use the port assigned by Railway
    
    # Detectar si estamos en Railway
    is_railway = os.environ.get('RAILWAY_ENVIRONMENT') is not None
    
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
