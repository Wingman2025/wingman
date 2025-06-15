"""
Simple seed para crear datos iniciales de Companion App
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Configuración básica de Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///wingfoil.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()
db.init_app(app)

# Definir modelos básicos necesarios
class GoalTemplate(db.Model):
    __tablename__ = 'goal_template'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)
    difficulty_level = db.Column(db.String(20), nullable=False)
    estimated_duration_days = db.Column(db.Integer)
    icon = db.Column(db.String(50))
    target_type = db.Column(db.String(20), nullable=False)
    default_target_value = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Badge(db.Model):
    __tablename__ = 'badge'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50))
    category = db.Column(db.String(50), nullable=False)
    criteria = db.Column(db.Text)
    points_value = db.Column(db.Integer, default=10)
    rarity = db.Column(db.String(20), default='common')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def create_sample_data():
    with app.app_context():
        # Crear algunas plantillas de objetivos
        templates = [
            {
                'title': 'Dominar el Jibe',
                'description': 'Conseguir realizar jibes consistentes',
                'category': 'technique',
                'difficulty_level': 'intermediate',
                'estimated_duration_days': 30,
                'icon': 'turn-right',
                'target_type': 'count',
                'default_target_value': 10
            },
            {
                'title': 'Sesión de 2 Horas',
                'description': 'Mantener una sesión activa de 2 horas',
                'category': 'endurance',
                'difficulty_level': 'intermediate',
                'estimated_duration_days': 14,
                'icon': 'clock',
                'target_type': 'duration',
                'default_target_value': 120
            }
        ]
        
        for template_data in templates:
            existing = GoalTemplate.query.filter_by(title=template_data['title']).first()
            if not existing:
                template = GoalTemplate(**template_data)
                db.session.add(template)
        
        # Crear algunos badges
        badges = [
            {
                'name': 'Primera Sesión',
                'description': 'Completaste tu primera sesión',
                'icon': 'play-circle',
                'category': 'milestone',
                'criteria': 'Completar 1 sesión',
                'points_value': 10,
                'rarity': 'common'
            },
            {
                'name': 'Primer Jibe',
                'description': 'Realizaste tu primer jibe exitoso',
                'icon': 'rotate-cw',
                'category': 'technique',
                'criteria': 'Primer jibe registrado',
                'points_value': 50,
                'rarity': 'rare'
            }
        ]
        
        for badge_data in badges:
            existing = Badge.query.filter_by(name=badge_data['name']).first()
            if not existing:
                badge = Badge(**badge_data)
                db.session.add(badge)
        
        db.session.commit()
        print("✅ Datos de ejemplo creados exitosamente!")

if __name__ == "__main__":
    create_sample_data()
