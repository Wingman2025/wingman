"""
Database initialization script for PythonAnywhere deployment.
Run this script once after uploading your code to PythonAnywhere.
"""

import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

def init_db():
    # Get the database path
    db_path = os.path.join(os.path.dirname(__file__), 'wingfoil.db')

    # Connect to the database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Create tables
    conn.executescript('''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TEXT NOT NULL,
        name TEXT
    );

    CREATE TABLE IF NOT EXISTS skill (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        practice TEXT,
        category TEXT
    );

    CREATE TABLE IF NOT EXISTS session (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        sport_type TEXT NOT NULL,
        duration INTEGER NOT NULL,
        rating INTEGER,
        location TEXT,
        notes TEXT,
        skills TEXT,
        skill_ratings TEXT,
        FOREIGN KEY (user_id) REFERENCES user (id)
    );
    ''')

    # Check if we already have a demo user
    cursor = conn.execute('SELECT COUNT(*) FROM user WHERE username = ?', ('demo',))
    if cursor.fetchone()[0] == 0:
        # Create a demo user
        conn.execute(
            'INSERT INTO user (username, email, password, created_at, name) VALUES (?, ?, ?, ?, ?)',
            ('demo', 'demo@example.com', generate_password_hash('password'), 
             datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Demo User')
        )
        print("Created demo user (username: demo, password: password)")

    # Check if skills already exist
    cursor = conn.execute('SELECT COUNT(*) FROM skill')
    count = cursor.fetchone()[0]

    # Add skills if none exist
    if count == 0:
        skills = [
            ('Waterstart', 'Getting up on the board from the water', 'Practice in light winds first', 'Beginner'),
            ('Tack', 'Changing direction by turning into the wind', 'Practice in moderate winds', 'Intermediate'),
            ('Jibe', 'Changing direction by turning downwind', 'Practice in moderate winds', 'Intermediate'),
            ('Riding Toeside', 'Riding with toes facing downwind', 'Practice in light winds first', 'Intermediate'),
            ('Riding Switch', 'Riding in the opposite stance', 'Practice in light winds first', 'Advanced'),
            ('Jump', 'Getting air off the water', 'Practice in stronger winds', 'Advanced'),
            ('Carving Turn', 'Smooth turn while maintaining speed', 'Practice in moderate winds', 'Intermediate'),
            ('Pump', 'Generating speed by pumping the wing', 'Practice in light winds', 'Beginner'),
            ('Foil Touch & Go', 'Briefly touching down with the foil', 'Practice in moderate winds', 'Advanced'),
            ('Foot Switch', 'Changing foot position while riding', 'Practice in moderate winds', 'Advanced')
        ]
        
        for skill in skills:
            conn.execute('''
            INSERT INTO skill (name, description, practice, category)
            VALUES (?, ?, ?, ?)
            ''', skill)
        
        print(f"Added {len(skills)} skills to the database")

    # Commit changes and close connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")
