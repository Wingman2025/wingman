#!/usr/bin/env python3
"""
Seed script optimizado para Railway - Companion App Motivacional
Ejecuta: python seed_railway.py
"""

import os
import sys
from datetime import datetime

# Agregar el directorio actual al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import app
from backend.models.legacy import db, GoalTemplate, Badge

def seed_goal_templates():
    """Crear plantillas de objetivos"""
    templates = [
        {
            'title': 'Dominar el Jibe',
            'description': 'Conseguir realizar jibes consistentes sin perder velocidad',
            'category': 'technique',
            'difficulty_level': 'intermediate',
            'estimated_duration_days': 30,
            'icon': 'turn-right',
            'target_type': 'count',
            'default_target_value': 10,
            'created_at': datetime.utcnow()
        },
        {
            'title': 'Primeros Saltos',
            'description': 'Realizar tus primeros saltos controlados',
            'category': 'technique',
            'difficulty_level': 'intermediate',
            'estimated_duration_days': 45,
            'icon': 'trending-up',
            'target_type': 'count',
            'default_target_value': 5,
            'created_at': datetime.utcnow()
        },
        {
            'title': 'Sesión de 2 Horas',
            'description': 'Mantener una sesión activa de al menos 2 horas',
            'category': 'endurance',
            'difficulty_level': 'intermediate',
            'estimated_duration_days': 14,
            'icon': 'clock',
            'target_type': 'duration',
            'default_target_value': 120,
            'created_at': datetime.utcnow()
        },
        {
            'title': 'Racha de 7 Días',
            'description': 'Entrenar durante 7 días consecutivos',
            'category': 'consistency',
            'difficulty_level': 'beginner',
            'estimated_duration_days': 7,
            'icon': 'calendar',
            'target_type': 'count',
            'default_target_value': 7,
            'created_at': datetime.utcnow()
        }
    ]
    
    created_count = 0
    for template_data in templates:
        # Verificar si ya existe
        existing = GoalTemplate.query.filter_by(title=template_data['title']).first()
        if not existing:
            template = GoalTemplate(**template_data)
            db.session.add(template)
            created_count += 1
            print(f"✅ Creada plantilla: {template_data['title']}")
        else:
            print(f"⏭️  Ya existe plantilla: {template_data['title']}")
    
    return created_count

def seed_badges():
    """Crear badges"""
    badges = [
        {
            'name': 'Primera Sesión',
            'description': 'Completaste tu primera sesión de wingfoil',
            'icon': 'play-circle',
            'category': 'milestone',
            'criteria': 'Completar 1 sesión',
            'points_value': 10,
            'rarity': 'common',
            'is_active': True,
            'created_at': datetime.utcnow()
        },
        {
            'name': 'Primer Jibe',
            'description': 'Realizaste tu primer jibe exitoso',
            'icon': 'rotate-cw',
            'category': 'technique',
            'criteria': 'Primer jibe registrado',
            'points_value': 50,
            'rarity': 'rare',
            'is_active': True,
            'created_at': datetime.utcnow()
        },
        {
            'name': 'Guerrero del Fin de Semana',
            'description': 'Entrenaste ambos días del fin de semana',
            'icon': 'calendar-check',
            'category': 'consistency',
            'criteria': 'Sesiones en sábado y domingo',
            'points_value': 30,
            'rarity': 'common',
            'is_active': True,
            'created_at': datetime.utcnow()
        },
        {
            'name': 'Racha de Fuego',
            'description': 'Entrenaste 7 días consecutivos',
            'icon': 'flame',
            'category': 'consistency',
            'criteria': '7 días consecutivos con sesiones',
            'points_value': 100,
            'rarity': 'epic',
            'is_active': True,
            'created_at': datetime.utcnow()
        },
        {
            'name': 'Objetivo Cumplido',
            'description': 'Completaste tu primer objetivo',
            'icon': 'target',
            'category': 'achievement',
            'criteria': 'Completar 1 objetivo',
            'points_value': 50,
            'rarity': 'common',
            'is_active': True,
            'created_at': datetime.utcnow()
        }
    ]
    
    created_count = 0
    for badge_data in badges:
        # Verificar si ya existe
        existing = Badge.query.filter_by(name=badge_data['name']).first()
        if not existing:
            badge = Badge(**badge_data)
            db.session.add(badge)
            created_count += 1
            print(f"✅ Creado badge: {badge_data['name']}")
        else:
            print(f"⏭️  Ya existe badge: {badge_data['name']}")
    
    return created_count

def main():
    """Función principal"""
    print("🌱 Iniciando seed para Companion App...")
    
    # Detectar entorno
    is_railway = os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RAILWAY_STATIC_URL')
    env_name = "Railway" if is_railway else "Local"
    print(f"🌍 Entorno detectado: {env_name}")
    
    try:
        with app.app_context():
            print("🔗 Conectado a la base de datos")
            
            # Verificar estado actual
            current_templates = GoalTemplate.query.count()
            current_badges = Badge.query.count()
            print(f"📊 Estado inicial: {current_templates} plantillas, {current_badges} badges")
            
            # Crear plantillas
            print("\n📋 Creando plantillas de objetivos...")
            templates_created = seed_goal_templates()
            
            # Crear badges
            print("\n🏆 Creando badges...")
            badges_created = seed_badges()
            
            # Guardar cambios
            if templates_created > 0 or badges_created > 0:
                db.session.commit()
                print(f"\n💾 Guardados {templates_created} plantillas y {badges_created} badges")
            else:
                print("\n💾 No hay cambios que guardar")
            
            # Estado final
            final_templates = GoalTemplate.query.count()
            final_badges = Badge.query.count()
            print(f"📊 Estado final: {final_templates} plantillas, {final_badges} badges")
            
            print("\n🎉 Seed completado exitosamente!")
            
    except Exception as e:
        print(f"\n❌ Error durante el seed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
