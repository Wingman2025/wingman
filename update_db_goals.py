import sqlite3
import os
from datetime import datetime

def update_database():
    """Update the database with a new goals table for the goal-setting feature"""
    db_path = 'wingfoil.db'
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    
    # Create goals table if it doesn't exist
    db.execute('''
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        target_date TEXT NOT NULL,
        completed INTEGER DEFAULT 0,
        progress INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        completed_at TEXT,
        FOREIGN KEY (user_id) REFERENCES user (id)
    )
    ''')
    
    conn.commit()
    print("Database updated successfully with goals table!")
    conn.close()

if __name__ == "__main__":
    update_database()
