"""
Script para aplicar migraciones y seed de Companion App en Railway
"""

import os
import sys
from app import app
from models import db, GoalTemplate, Badge
from datetime import datetime

def apply_migrations():
    """Aplicar migraciones pendientes"""
    print("🔄 Aplicando migraciones...")
    with app.app_context():
        # Crear todas las tablas si no existen
        db.create_all()
        print("✅ Migraciones aplicadas")

def seed_companion_data():
    """Poblar datos iniciales de Companion App"""
    with app.app_context():
        print("🌱 Iniciando seed de datos para Companion App...")
        
        # Verificar si ya existen datos
        existing_templates = GoalTemplate.query.count()
        existing_badges = Badge.query.count()
        
        if existing_templates > 0 and existing_badges > 0:
            print(f"ℹ️  Ya existen {existing_templates} plantillas y {existing_badges} badges")
            return
        
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

def main():
    """Función principal para Railway"""
    print("🚀 Iniciando deployment de Companion App en Railway...")
    
    # Verificar que estamos en Railway
    is_railway = os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RAILWAY_STATIC_URL')
    if is_railway:
        print("🚂 Detectado entorno Railway")
    else:
        print("💻 Ejecutando en entorno local")
    
    try:
        apply_migrations()
        seed_companion_data()
        print("🎯 Deployment de Companion App completado exitosamente!")
        
        # Verificar que todo funciona
        with app.app_context():
            templates_count = GoalTemplate.query.count()
            badges_count = Badge.query.count()
            print(f"📊 Estado final: {templates_count} plantillas, {badges_count} badges")
            
    except Exception as e:
        print(f"❌ Error durante el deployment: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
