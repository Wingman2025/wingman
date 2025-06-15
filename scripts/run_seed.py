"""
Script para ejecutar seed usando el contexto de la aplicación principal
"""

from app import app
from backend.models.legacy import db, GoalTemplate, Badge
from datetime import datetime
# Ensure project root in sys.path
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def seed_data():
    with app.app_context():
        print("🌱 Iniciando seed de datos para Companion App...")
        
        # Crear plantillas de objetivos
        goal_templates = [
            {
                'title': 'Dominar el Jibe',
                'description': 'Conseguir realizar jibes consistentes sin perder velocidad',
                'category': 'technique',
                'difficulty_level': 'intermediate',
                'estimated_duration_days': 30,
                'icon': 'turn-right',
                'target_type': 'count',
                'default_target_value': 10
            },
            {
                'title': 'Primeros Saltos',
                'description': 'Realizar tus primeros saltos controlados',
                'category': 'technique',
                'difficulty_level': 'intermediate',
                'estimated_duration_days': 45,
                'icon': 'trending-up',
                'target_type': 'count',
                'default_target_value': 5
            },
            {
                'title': 'Sesión de 2 Horas',
                'description': 'Mantener una sesión activa de al menos 2 horas',
                'category': 'endurance',
                'difficulty_level': 'intermediate',
                'estimated_duration_days': 14,
                'icon': 'clock',
                'target_type': 'duration',
                'default_target_value': 120
            },
            {
                'title': 'Racha de 7 Días',
                'description': 'Entrenar durante 7 días consecutivos',
                'category': 'consistency',
                'difficulty_level': 'beginner',
                'estimated_duration_days': 7,
                'icon': 'calendar',
                'target_type': 'count',
                'default_target_value': 7
            }
        ]
        
        for template_data in goal_templates:
            existing = GoalTemplate.query.filter_by(title=template_data['title']).first()
            if not existing:
                template = GoalTemplate(**template_data)
                db.session.add(template)
        
        # Crear badges
        badges = [
            {
                'name': 'Primera Sesión',
                'description': 'Completaste tu primera sesión de wingfoil',
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
            },
            {
                'name': 'Guerrero del Fin de Semana',
                'description': 'Entrenaste ambos días del fin de semana',
                'icon': 'calendar-check',
                'category': 'consistency',
                'criteria': 'Sesiones en sábado y domingo',
                'points_value': 30,
                'rarity': 'common'
            },
            {
                'name': 'Racha de Fuego',
                'description': 'Entrenaste 7 días consecutivos',
                'icon': 'flame',
                'category': 'consistency',
                'criteria': '7 días consecutivos con sesiones',
                'points_value': 100,
                'rarity': 'epic'
            },
            {
                'name': 'Objetivo Cumplido',
                'description': 'Completaste tu primer objetivo',
                'icon': 'target',
                'category': 'achievement',
                'criteria': 'Completar 1 objetivo',
                'points_value': 50,
                'rarity': 'common'
            }
        ]
        
        for badge_data in badges:
            existing = Badge.query.filter_by(name=badge_data['name']).first()
            if not existing:
                badge = Badge(**badge_data)
                db.session.add(badge)
        
        db.session.commit()
        print(f"✅ Creadas {len(goal_templates)} plantillas de objetivos")
        print(f"✅ Creados {len(badges)} badges")
        print("🎉 Seed completado exitosamente!")

if __name__ == "__main__":
    seed_data()
