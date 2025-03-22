import os
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
            from railway_init import init_railway_db
            init_railway_db()
        else:
            # En entorno local, usar la inicialización estándar
            initialize_database()
    
    app.run(debug=False, host='0.0.0.0', port=port)
