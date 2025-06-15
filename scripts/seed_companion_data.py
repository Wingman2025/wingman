"""
Seed data para Companion App Motivacional
Crea plantillas de objetivos y badges iniciales
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app import app
from backend.models.legacy import db, GoalTemplate, Badge
from datetime import datetime

def seed_goal_templates():
    """Crear plantillas de objetivos predefinidos"""
    
    goal_templates = [
        # Objetivos de Técnica
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
            'title': 'Waterstart Consistente',
            'description': 'Conseguir waterstart exitoso en 9 de cada 10 intentos',
            'category': 'technique',
            'difficulty_level': 'beginner',
            'estimated_duration_days': 21,
            'icon': 'play',
            'target_type': 'count',
            'default_target_value': 20
        },
        
        # Objetivos de Resistencia
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
            'title': 'Vuelo Continuo 30min',
            'description': 'Volar de forma continua durante 30 minutos sin caer',
            'category': 'endurance',
            'difficulty_level': 'advanced',
            'estimated_duration_days': 60,
            'icon': 'wind',
            'target_type': 'duration',
            'default_target_value': 30
        },
        
        # Objetivos de Progresión
        {
            'title': 'Subir de Nivel',
            'description': 'Avanzar al siguiente nivel de wingfoil',
            'category': 'progression',
            'difficulty_level': 'intermediate',
            'estimated_duration_days': 90,
            'icon': 'arrow-up',
            'target_type': 'boolean',
            'default_target_value': 1
        },
        {
            'title': 'Navegar en Viento Fuerte',
            'description': 'Conseguir navegar cómodamente con viento de 20+ nudos',
            'category': 'progression',
            'difficulty_level': 'advanced',
            'estimated_duration_days': 120,
            'icon': 'zap',
            'target_type': 'count',
            'default_target_value': 5
        },
        
        # Objetivos de Consistencia
        {
            'title': 'Racha de 7 Días',
            'description': 'Entrenar durante 7 días consecutivos',
            'category': 'consistency',
            'difficulty_level': 'beginner',
            'estimated_duration_days': 7,
            'icon': 'calendar',
            'target_type': 'count',
            'default_target_value': 7
        },
        {
            'title': '20 Sesiones en un Mes',
            'description': 'Completar 20 sesiones de entrenamiento en 30 días',
            'category': 'consistency',
            'difficulty_level': 'intermediate',
            'estimated_duration_days': 30,
            'icon': 'repeat',
            'target_type': 'count',
            'default_target_value': 20
        }
    ]
    
    for template_data in goal_templates:
        # Verificar si ya existe
        existing = GoalTemplate.query.filter_by(title=template_data['title']).first()
        if not existing:
            template = GoalTemplate(**template_data)
            db.session.add(template)
    
    db.session.commit()
    print(f"✅ Creadas {len(goal_templates)} plantillas de objetivos")

def seed_badges():
    """Crear badges iniciales del sistema"""
    
    badges = [
        # Badges de Primeros Pasos
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
            'name': 'Primer Waterstart',
            'description': 'Conseguiste tu primer waterstart exitoso',
            'icon': 'droplet',
            'category': 'technique',
            'criteria': 'Primer waterstart registrado',
            'points_value': 25,
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
        
        # Badges de Consistencia
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
            'name': 'Adicto al Wingfoil',
            'description': 'Completaste 50 sesiones',
            'icon': 'heart',
            'category': 'milestone',
            'criteria': '50 sesiones completadas',
            'points_value': 200,
            'rarity': 'epic'
        },
        
        # Badges de Progreso Técnico
        {
            'name': 'Maestro del Jibe',
            'description': 'Realizaste 25 jibes exitosos',
            'icon': 'award',
            'category': 'technique',
            'criteria': '25 jibes registrados',
            'points_value': 150,
            'rarity': 'rare'
        },
        {
            'name': 'Volador',
            'description': 'Acumulaste 10 horas de vuelo',
            'icon': 'feather',
            'category': 'endurance',
            'criteria': '600 minutos de vuelo total',
            'points_value': 100,
            'rarity': 'rare'
        },
        {
            'name': 'Saltador',
            'description': 'Realizaste tu primer salto',
            'icon': 'trending-up',
            'category': 'technique',
            'criteria': 'Primer salto registrado',
            'points_value': 75,
            'rarity': 'rare'
        },
        
        # Badges de Motivación
        {
            'name': 'Energía Positiva',
            'description': 'Mantuviste alta motivación en 10 sesiones',
            'icon': 'smile',
            'category': 'motivation',
            'criteria': 'Motivación ≥8 en 10 sesiones',
            'points_value': 80,
            'rarity': 'rare'
        },
        {
            'name': 'Objetivo Cumplido',
            'description': 'Completaste tu primer objetivo',
            'icon': 'target',
            'category': 'achievement',
            'criteria': 'Completar 1 objetivo',
            'points_value': 50,
            'rarity': 'common'
        },
        {
            'name': 'Coleccionista de Objetivos',
            'description': 'Completaste 5 objetivos diferentes',
            'icon': 'collection',
            'category': 'achievement',
            'criteria': 'Completar 5 objetivos',
            'points_value': 250,
            'rarity': 'legendary'
        },
        
        # Badges Especiales
        {
            'name': 'Madrugador',
            'description': 'Entrenaste antes de las 8:00 AM',
            'icon': 'sunrise',
            'category': 'special',
            'criteria': 'Sesión antes de las 8:00',
            'points_value': 40,
            'rarity': 'common'
        },
        {
            'name': 'Guerrero de Viento',
            'description': 'Entrenaste con viento de más de 25 nudos',
            'icon': 'wind',
            'category': 'special',
            'criteria': 'Sesión con viento >25 nudos',
            'points_value': 120,
            'rarity': 'epic'
        },
        {
            'name': 'Explorador',
            'description': 'Entrenaste en 5 spots diferentes',
            'icon': 'map-pin',
            'category': 'exploration',
            'criteria': '5 ubicaciones diferentes',
            'points_value': 90,
            'rarity': 'rare'
        }
    ]
    
    for badge_data in badges:
        # Verificar si ya existe
        existing = Badge.query.filter_by(name=badge_data['name']).first()
        if not existing:
            badge = Badge(**badge_data)
            db.session.add(badge)
    
    db.session.commit()
    print(f"✅ Creados {len(badges)} badges")

def run_seed():
    """Ejecutar todas las funciones de seed"""
    print("🌱 Iniciando seed de datos para Companion App...")
    seed_goal_templates()
    seed_badges()
    print("🎉 Seed completado exitosamente!")

if __name__ == "__main__":
    # Para ejecutar directamente
    with app.app_context():
        run_seed()
