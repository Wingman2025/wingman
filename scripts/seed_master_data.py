"""
Script: seed_master_data.py
Propósito: Cargar datos maestros (plantillas de objetivos y badges) en cualquier entorno (dev, staging, prod) de forma idempotente.
Uso:
    python seed_master_data.py
    # o en Railway:
    railway run python seed_master_data.py
"""
from app import app, db
from backend.models.legacy import GoalTemplate, Badge
from datetime import datetime
# Ensure project root in sys.path
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


TEMPLATES_DATA = [
    {
        'title': 'Dominar el Jibe',
        'description': 'Perfecciona tu técnica de jibe para cambios de dirección fluidos',
        'category': 'tecnica',
        'difficulty_level': 'intermedio',
        'estimated_duration_days': 30,
        'icon': '🌊',
        'target_type': 'count',
        'default_target_value': 10
    },
    {
        'title': 'Primeros Saltos',
        'description': 'Aprende a saltar y aterrizar de forma segura',
        'category': 'freestyle',
        'difficulty_level': 'intermedio',
        'estimated_duration_days': 45,
        'icon': '🚀',
        'target_type': 'count',
        'default_target_value': 5
    },
    {
        'title': 'Sesión de 2 Horas',
        'description': 'Mantén una sesión continua de 2 horas en el agua',
        'category': 'resistencia',
        'difficulty_level': 'principiante',
        'estimated_duration_days': 14,
        'icon': '⏱️',
        'target_type': 'duration',
        'default_target_value': 120
    },
    {
        'title': 'Racha de 7 Días',
        'description': 'Practica wingfoil durante 7 días consecutivos',
        'category': 'consistencia',
        'difficulty_level': 'principiante',
        'estimated_duration_days': 7,
        'icon': '🔥',
        'target_type': 'streak',
        'default_target_value': 7
    }
]

BADGES_DATA = [
    {
        'name': 'Primera Sesión',
        'description': 'Completaste tu primera sesión de wingfoil',
        'icon': '🎯',
        'category': 'inicio',
        'criteria': 'Completar 1 sesión',
        'points_value': 10,
        'rarity': 'comun'
    },
    {
        'name': 'Primer Jibe',
        'description': 'Realizaste tu primer jibe exitoso',
        'icon': '🌊',
        'category': 'tecnica',
        'criteria': 'Realizar 1 jibe',
        'points_value': 25,
        'rarity': 'poco_comun'
    },
    {
        'name': 'Guerrero del Fin de Semana',
        'description': 'Practica wingfoil todos los fines de semana del mes',
        'icon': '⚔️',
        'category': 'consistencia',
        'criteria': 'Sesiones en 4 fines de semana consecutivos',
        'points_value': 50,
        'rarity': 'raro'
    },
    {
        'name': 'Racha de Fuego',
        'description': 'Mantén una racha de 10 días consecutivos',
        'icon': '🔥',
        'category': 'consistencia',
        'criteria': 'Sesiones en 10 días consecutivos',
        'points_value': 75,
        'rarity': 'epico'
    },
    {
        'name': 'Objetivo Cumplido',
        'description': 'Completa tu primer objetivo personal',
        'icon': '🏆',
        'category': 'logro',
        'criteria': 'Completar 1 objetivo',
        'points_value': 30,
        'rarity': 'poco_comun'
    }
]

def seed_master_data():
    with app.app_context():
        templates_created = 0
        for template_data in TEMPLATES_DATA:
            existing = GoalTemplate.query.filter_by(title=template_data['title']).first()
            if not existing:
                template = GoalTemplate(**template_data)
                db.session.add(template)
                templates_created += 1
        badges_created = 0
        for badge_data in BADGES_DATA:
            existing = Badge.query.filter_by(name=badge_data['name']).first()
            if not existing:
                badge = Badge(**badge_data)
                db.session.add(badge)
                badges_created += 1
        if templates_created > 0 or badges_created > 0:
            db.session.commit()
            print(f"✅ Seed completado: {templates_created} plantillas, {badges_created} badges creados")
        else:
            print("ℹ️  Todos los datos ya existían")
        final_templates = GoalTemplate.query.count()
        final_badges = Badge.query.count()
        print(f"📊 Estado final: {final_templates} plantillas, {final_badges} badges")

if __name__ == "__main__":
    seed_master_data()
