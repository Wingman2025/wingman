"""
Script para actualizar la estructura de la tabla usuario en la base de datos.
"""

import sqlite3
import os

def update_user_table():
    # Conectar a la base de datos
    db_path = os.path.join(os.path.dirname(__file__), 'wingfoil.db')
    print(f"Conectando a la base de datos: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Verificar la estructura actual de la tabla user
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(user)")
    current_columns = [row[1] for row in cursor.fetchall()]
    print(f"Columnas actuales en la tabla user: {current_columns}")
    
    # Columnas que deberían estar en la tabla según el código
    required_columns = {
        'name': 'TEXT',
        'wingfoil_level': 'TEXT'
    }
    
    # Añadir las columnas faltantes
    for column, column_type in required_columns.items():
        if column not in current_columns:
            print(f"Añadiendo columna {column} a la tabla user...")
            try:
                cursor.execute(f"ALTER TABLE user ADD COLUMN {column} {column_type}")
                print(f"Columna {column} añadida correctamente.")
            except sqlite3.Error as e:
                print(f"Error al añadir columna {column}: {e}")
    
    conn.commit()
    print("Actualización de la tabla user completada.")
    
    # Verificar la estructura actualizada
    cursor.execute("PRAGMA table_info(user)")
    updated_columns = [row[1] for row in cursor.fetchall()]
    print(f"Columnas actualizadas en la tabla user: {updated_columns}")
    
    # Cerrar la conexión
    conn.close()

if __name__ == '__main__':
    update_user_table()
    print("Script completado con éxito.")
