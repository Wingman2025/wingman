import sqlite3
import os

def update_database():
    """Update the database with new tables and columns for user profiles and goals"""
    db_path = 'wingfoil.db'
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    
    # Check if user table has profile_picture column
    cursor = db.execute("PRAGMA table_info(user)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'profile_picture' not in columns:
        print("Adding profile_picture column to user table...")
        db.execute("ALTER TABLE user ADD COLUMN profile_picture TEXT")
    
    if 'avatar_choice' not in columns:
        print("Adding avatar_choice column to user table...")
        db.execute("ALTER TABLE user ADD COLUMN avatar_choice TEXT DEFAULT 'default'")
    
    # Create goals table if it doesn't exist
    db.execute('''
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        target_date TEXT,
        completed INTEGER DEFAULT 0,
        progress INTEGER DEFAULT 0,
        category TEXT,
        created_at TEXT NOT NULL,
        completed_at TEXT,
        FOREIGN KEY (user_id) REFERENCES user (id)
    )
    ''')
    
    # Create skill_progress table to track user progress in skills
    db.execute('''
    CREATE TABLE IF NOT EXISTS skill_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        skill_id INTEGER NOT NULL,
        progress INTEGER DEFAULT 0,
        last_updated TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES user (id),
        FOREIGN KEY (skill_id) REFERENCES skill (id),
        UNIQUE(user_id, skill_id)
    )
    ''')
    
    conn.commit()
    print("Database updated successfully!")
    conn.close()

if __name__ == "__main__":
    update_database()
