"""
Script de inicialización para Railway.
Este script se ejecutará automáticamente en el entorno de Railway para configurar la base de datos.
"""

import os
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

def init_railway_db():
    print("Iniciando configuración de base de datos para Railway...")
    
    # Obtener la ruta de la base de datos
    db_path = os.path.join(os.path.dirname(__file__), 'wingfoil.db')
    print(f"Ruta de la base de datos: {db_path}")
    
    # Verificar si el directorio existe
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Conectar a la base de datos
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Crear tablas
    print("Creando tablas si no existen...")
    conn.executescript('''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        profile_picture TEXT,
        nationality TEXT,
        age INTEGER,
        sports_practiced TEXT,
        location TEXT,
        wingfoiling_since TEXT,
        wingfoil_level TEXT,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        name TEXT
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
        achievements TEXT,
        challenges TEXT,
        conditions TEXT,
        weather TEXT,
        wind_speed TEXT,
        equipment TEXT,
        water_conditions TEXT,
        FOREIGN KEY (user_id) REFERENCES user (id)
    );

    CREATE TABLE IF NOT EXISTS skill (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        tips TEXT,
        video_url TEXT,
        difficulty TEXT,
        practice TEXT,
        equipment TEXT,
        learning_time TEXT
    );

    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        target_date TEXT,
        status TEXT NOT NULL DEFAULT 'In Progress',
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        skill_id INTEGER,
        completed BOOLEAN DEFAULT 0,
        progress INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES user (id),
        FOREIGN KEY (skill_id) REFERENCES skill (id)
    );
    ''')
    
    # Verificar si hay habilidades en la base de datos
    cursor = conn.execute('SELECT COUNT(*) FROM skill')
    count = cursor.fetchone()[0]
    
    # Añadir habilidades si no existen
    if count == 0:
        print("Añadiendo habilidades a la base de datos...")
        skills = [
            {
                'name': 'Wing Handling & Depowering',
                'description': 'Mastering your wing\'s power - knowing how to generate lift and quickly depower by turning the wing out of the wind - is fundamental for control.',
                'practice': 'Start in calm, low-wind conditions on land or shallow water; work on smoothly adjusting the wing\'s angle and quickly depowering when needed.',
                'category': 'Basic',
                'tips': 'Keep your arms slightly bent and use your body rotation for better control.',
                'difficulty': 'Beginner',
                'equipment': 'Any wing size suitable for your weight and wind conditions',
                'learning_time': '1-2 sessions'
            },
            {
                'name': 'Water Start',
                'description': 'Learning to properly get up on your board from a floating position in the water using the wing for balance and power.',
                'practice': 'Practice in waist-deep water first, then gradually move to deeper water. Focus on board positioning and wing control.',
                'category': 'Basic',
                'tips': 'Position your board perpendicular to the wind direction for easier starts.',
                'difficulty': 'Beginner',
                'equipment': 'Larger, more stable board for beginners',
                'learning_time': '2-3 sessions'
            },
            {
                'name': 'Upwind Riding',
                'description': 'The ability to ride against the direction of the wind, which is essential for returning to your starting point without walking or swimming.',
                'practice': 'Focus on proper body position, board angle, and wing control. Start with short upwind segments and build up.',
                'category': 'Basic',
                'tips': 'Lean slightly upwind and keep your weight on your heels for better upwind angle.',
                'difficulty': 'Beginner-Intermediate',
                'equipment': 'Standard board and wing setup',
                'learning_time': '5-10 sessions'
            },
            {
                'name': 'Tacking',
                'description': 'Changing direction by turning the board through the wind while maintaining forward momentum.',
                'practice': 'Practice in moderate wind conditions, focusing on smooth board rotation and wing repositioning.',
                'category': 'Intermediate',
                'tips': 'Keep the wing powered until the last moment, then switch hands smoothly.',
                'difficulty': 'Intermediate',
                'equipment': 'Standard board and wing setup',
                'learning_time': '3-5 sessions'
            },
            {
                'name': 'Jibing',
                'description': 'Changing direction by turning downwind, which is generally faster and more dynamic than tacking.',
                'practice': 'Begin with wide, gradual turns and work towards tighter, faster jibes as your confidence grows.',
                'category': 'Intermediate',
                'tips': 'Use your body weight to initiate the turn and keep your eyes on the direction you want to go.',
                'difficulty': 'Intermediate',
                'equipment': 'Standard board and wing setup',
                'learning_time': '4-6 sessions'
            },
            {
                'name': 'Riding Toeside',
                'description': 'Riding with your toes facing the direction of travel, which opens up new dimensions of maneuvering.',
                'practice': 'Start with short toeside segments, gradually increasing duration and comfort.',
                'category': 'Intermediate',
                'tips': 'Keep your weight centered and knees bent for better balance.',
                'difficulty': 'Intermediate',
                'equipment': 'Standard board and wing setup',
                'learning_time': '3-5 sessions'
            },
            {
                'name': 'Small Jumps',
                'description': 'Getting airborne for short periods, which is the foundation for more advanced aerial maneuvers.',
                'practice': 'Start with small chop or waves, focus on timing and light landings.',
                'category': 'Advanced',
                'tips': 'Use your legs as shock absorbers for landings and keep the wing powered for stability.',
                'difficulty': 'Advanced',
                'equipment': 'Standard board and wing setup, helmet recommended',
                'learning_time': '5-10 sessions'
            },
            {
                'name': 'Foil Touches',
                'description': 'Briefly lifting the foil out of the water and reinserting it smoothly, a stepping stone to foil jumping.',
                'practice': 'Practice in flat water with consistent wind, focusing on controlled lift and reentry.',
                'category': 'Advanced',
                'tips': 'Use subtle body movements rather than dramatic shifts in weight.',
                'difficulty': 'Advanced',
                'equipment': 'Standard board and foil setup',
                'learning_time': '8-12 sessions'
            },
            {
                'name': 'Wing 360',
                'description': 'A full 360-degree rotation while riding, combining both balance and wing control for a stylish maneuver.',
                'practice': 'Start with wide, slow rotations and gradually increase speed and tightness.',
                'category': 'Advanced',
                'tips': 'Keep your eyes scanning through the rotation to maintain orientation.',
                'difficulty': 'Advanced',
                'equipment': 'Standard board and wing setup',
                'learning_time': '10-15 sessions'
            }
        ]
        
        for skill in skills:
            conn.execute('''
            INSERT INTO skill (name, category, description, practice, tips, difficulty, equipment, learning_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                skill['name'],
                skill['category'],
                skill['description'],
                skill.get('practice', ''),
                skill.get('tips', ''),
                skill.get('difficulty', ''),
                skill.get('equipment', ''),
                skill.get('learning_time', '')
            ))
        
        conn.commit()
        print(f"Se han añadido {len(skills)} habilidades a la base de datos.")
    
    # Cerrar la conexión
    conn.close()
    print("Configuración de base de datos para Railway completada.")

if __name__ == "__main__":
    init_railway_db()
