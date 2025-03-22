"""
Script para inicializar manualmente la base de datos en Railway.
Este script puede ser ejecutado directamente en la consola de Railway para forzar la inicialización de la base de datos.
"""

import os
import sqlite3
import sys

def force_init_db():
    print("=== INICIALIZACIÓN FORZADA DE LA BASE DE DATOS EN RAILWAY ===")
    
    # Importar el script de inicialización de Railway
    try:
        from railway_init import init_railway_db
        
        # Ejecutar la inicialización
        print("Ejecutando inicialización de Railway...")
        init_railway_db()
        print("Inicialización completada con éxito.")
        
        # Verificar que las tablas existen
        db_path = os.path.join(os.path.dirname(__file__), 'wingfoil.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # Verificar tabla skill
        result = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='skill'").fetchone()
        if result:
            print("✅ Tabla 'skill' existe en la base de datos")
            # Contar habilidades
            count = conn.execute("SELECT COUNT(*) FROM skill").fetchone()[0]
            print(f"✅ Número de habilidades en la base de datos: {count}")
        else:
            print("❌ ERROR: La tabla 'skill' NO existe en la base de datos")
        
        # Verificar otras tablas importantes
        tables = ['user', 'session', 'goals']
        for table in tables:
            result = conn.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'").fetchone()
            if result:
                print(f"✅ Tabla '{table}' existe en la base de datos")
            else:
                print(f"❌ ERROR: La tabla '{table}' NO existe en la base de datos")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ ERROR durante la inicialización: {e}")
        print(f"Tipo de error: {type(e)}")
        print(f"Detalles del error: {sys.exc_info()}")
        return False
    
    return True

if __name__ == "__main__":
    success = force_init_db()
    if success:
        print("✅ Inicialización manual completada con éxito.")
    else:
        print("❌ La inicialización manual falló. Revise los errores anteriores.")
        sys.exit(1)
