import sqlite3
import os

def update_db():
    """Update the database schema to add missing columns."""
    db_path = os.path.join(os.path.dirname(__file__), 'wingfoil.db')
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Check if user_id column exists in session table
    cursor = conn.execute("PRAGMA table_info(session)")
    columns = [column['name'] for column in cursor.fetchall()]
    
    # Add user_id column if it doesn't exist
    if 'user_id' not in columns:
        print("Adding user_id column to session table...")
        try:
            conn.execute("ALTER TABLE session ADD COLUMN user_id INTEGER")
            # Set a default user_id for existing records (use 1 for the first user)
            conn.execute("UPDATE session SET user_id = 1")
            conn.commit()
            print("Successfully added user_id column and updated existing records.")
        except Exception as e:
            print(f"Error updating database: {e}")
            conn.rollback()
    else:
        print("user_id column already exists in session table.")
    
    # Close the connection
    conn.close()

if __name__ == '__main__':
    update_db()
