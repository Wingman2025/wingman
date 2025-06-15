"""
Companion App Motivacional - API Endpoints
Backend API para el sistema de objetivos y badges motivacionales
"""

from flask import Blueprint, request, jsonify, session
from models import db, User, GoalTemplate, UserGoal, Badge, UserBadge, Session
from datetime import datetime
import json

# Create blueprint for companion app API
companion_bp = Blueprint('companion', __name__)

# Helper function to get current user
def get_current_user():
    if 'user_id' not in session:
        return None
    return User.query.get(session['user_id'])

# Helper function for JSON responses
def json_response(data, status=200):
    return jsonify(data), status

def error_response(message, status=400):
    return jsonify({'error': message}), status

# ===== GOAL ENDPOINTS =====

@companion_bp.route('/api/user_goals', methods=['GET'])
def get_user_goals():
    """Obtener objetivos del usuario actual"""
    user = get_current_user()
    if not user:
        return error_response('Usuario no autenticado', 401)
    
    # Obtener objetivos activos del usuario
    user_goals = UserGoal.query.filter_by(user_id=user.id).all()
    
    goals_data = []
    for goal in user_goals:
        goal_data = {
            'id': goal.id,
            'title': goal.custom_title or (goal.goal_template.title if goal.goal_template else 'Objetivo personalizado'),
            'description': goal.custom_description or (goal.goal_template.description if goal.goal_template else ''),
            'target_value': goal.target_value,
            'current_progress': goal.current_progress,
            'progress_percentage': round((goal.current_progress / goal.target_value) * 100, 1) if goal.target_value > 0 else 0,
            'status': goal.status,
            'start_date': goal.start_date.isoformat() if goal.start_date else None,
            'target_date': goal.target_date.isoformat() if goal.target_date else None,
            'completed_date': goal.completed_date.isoformat() if goal.completed_date else None,
            'category': goal.goal_template.category if goal.goal_template else 'custom',
            'difficulty_level': goal.goal_template.difficulty_level if goal.goal_template else 'intermediate',
            'icon': goal.goal_template.icon if goal.goal_template else 'target'
        }
        goals_data.append(goal_data)
    
    return json_response({
        'goals': goals_data,
        'total_active': len([g for g in goals_data if g['status'] == 'active']),
        'total_completed': len([g for g in goals_data if g['status'] == 'completed'])
    })

@companion_bp.route('/api/goal_templates', methods=['GET'])
def get_goal_templates():
    """Obtener plantillas de objetivos disponibles"""
    templates = GoalTemplate.query.all()
    
    templates_data = []
    for template in templates:
        template_data = {
            'id': template.id,
            'title': template.title,
            'description': template.description,
            'category': template.category,
            'difficulty_level': template.difficulty_level,
            'estimated_duration_days': template.estimated_duration_days,
            'icon': template.icon,
            'target_type': template.target_type,
            'default_target_value': template.default_target_value
        }
        templates_data.append(template_data)
    
    return json_response({'templates': templates_data})

@companion_bp.route('/api/create_goal', methods=['POST'])
def create_goal():
    """Crear nuevo objetivo para el usuario"""
    user = get_current_user()
    if not user:
        return error_response('Usuario no autenticado', 401)
    
    data = request.get_json()
    if not data:
        return error_response('Datos requeridos', 400)
    
    # Validar campos requeridos
    if 'target_value' not in data:
        return error_response('target_value es requerido', 400)
    
    try:
        # Crear nuevo objetivo
        new_goal = UserGoal(
            user_id=user.id,
            goal_template_id=data.get('goal_template_id'),
            custom_title=data.get('custom_title'),
            custom_description=data.get('custom_description'),
            target_value=int(data['target_value']),
            target_date=datetime.fromisoformat(data['target_date']) if data.get('target_date') else None
        )
        
        db.session.add(new_goal)
        db.session.commit()
        
        return json_response({
            'message': 'Objetivo creado exitosamente',
            'goal_id': new_goal.id
        }, 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error al crear objetivo: {str(e)}', 500)

@companion_bp.route('/api/update_goal_progress', methods=['PATCH'])
def update_goal_progress():
    """Actualizar progreso de un objetivo"""
    user = get_current_user()
    if not user:
        return error_response('Usuario no autenticado', 401)
    
    data = request.get_json()
    if not data or 'goal_id' not in data:
        return error_response('goal_id es requerido', 400)
    
    try:
        # Buscar el objetivo
        goal = UserGoal.query.filter_by(id=data['goal_id'], user_id=user.id).first()
        if not goal:
            return error_response('Objetivo no encontrado', 404)
        
        # Actualizar progreso
        if 'current_progress' in data:
            goal.current_progress = int(data['current_progress'])
        
        if 'increment_progress' in data:
            goal.current_progress += int(data['increment_progress'])
        
        # Verificar si se completó el objetivo
        if goal.current_progress >= goal.target_value and goal.status == 'active':
            goal.status = 'completed'
            goal.completed_date = datetime.utcnow()
            
            # Aquí podrías disparar lógica para desbloquear badges
            # check_and_unlock_badges(user.id, goal)
        
        db.session.commit()
        
        return json_response({
            'message': 'Progreso actualizado exitosamente',
            'current_progress': goal.current_progress,
            'progress_percentage': round((goal.current_progress / goal.target_value) * 100, 1),
            'completed': goal.status == 'completed'
        })
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error al actualizar progreso: {str(e)}', 500)

# ===== BADGE ENDPOINTS =====

@companion_bp.route('/api/badges', methods=['GET'])
def get_badges():
    """Obtener badges disponibles y desbloqueados por el usuario"""
    user = get_current_user()
    if not user:
        return error_response('Usuario no autenticado', 401)
    
    # Obtener todos los badges activos
    all_badges = Badge.query.filter_by(is_active=True).all()
    
    # Obtener badges desbloqueados por el usuario
    user_badges = UserBadge.query.filter_by(user_id=user.id).all()
    unlocked_badge_ids = {ub.badge_id for ub in user_badges}
    
    badges_data = []
    for badge in all_badges:
        is_unlocked = badge.id in unlocked_badge_ids
        unlock_date = None
        
        if is_unlocked:
            user_badge = next((ub for ub in user_badges if ub.badge_id == badge.id), None)
            unlock_date = user_badge.unlocked_at.isoformat() if user_badge else None
        
        badge_data = {
            'id': badge.id,
            'name': badge.name,
            'description': badge.description,
            'icon': badge.icon,
            'category': badge.category,
            'points_value': badge.points_value,
            'rarity': badge.rarity,
            'is_unlocked': is_unlocked,
            'unlocked_at': unlock_date
        }
        badges_data.append(badge_data)
    
    # Calcular estadísticas
    total_badges = len(all_badges)
    unlocked_count = len(unlocked_badge_ids)
    total_points = sum(badge.points_value for badge in all_badges if badge.id in unlocked_badge_ids)
    
    return json_response({
        'badges': badges_data,
        'stats': {
            'total_badges': total_badges,
            'unlocked_count': unlocked_count,
            'completion_percentage': round((unlocked_count / total_badges) * 100, 1) if total_badges > 0 else 0,
            'total_points': total_points
        }
    })

@companion_bp.route('/api/unlock_badge', methods=['POST'])
def unlock_badge():
    """Desbloquear badge para el usuario"""
    user = get_current_user()
    if not user:
        return error_response('Usuario no autenticado', 401)
    
    data = request.get_json()
    if not data or 'badge_id' not in data:
        return error_response('badge_id es requerido', 400)
    
    try:
        # Verificar que el badge existe
        badge = Badge.query.get(data['badge_id'])
        if not badge:
            return error_response('Badge no encontrado', 404)
        
        # Verificar que el usuario no tenga ya este badge
        existing = UserBadge.query.filter_by(user_id=user.id, badge_id=badge.id).first()
        if existing:
            return error_response('Badge ya desbloqueado', 400)
        
        # Crear nuevo UserBadge
        user_badge = UserBadge(
            user_id=user.id,
            badge_id=badge.id,
            progress_when_unlocked=data.get('progress_context', '')
        )
        
        db.session.add(user_badge)
        db.session.commit()
        
        return json_response({
            'message': f'¡Badge "{badge.name}" desbloqueado!',
            'badge': {
                'id': badge.id,
                'name': badge.name,
                'description': badge.description,
                'points_value': badge.points_value,
                'rarity': badge.rarity
            }
        }, 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error al desbloquear badge: {str(e)}', 500)

# ===== SESSION TRACKING ENDPOINTS =====

@companion_bp.route('/api/session_stats', methods=['GET'])
def get_session_stats():
    """Obtener estadísticas de sesiones para motivación"""
    user = get_current_user()
    if not user:
        return error_response('Usuario no autenticado', 401)
    
    # Obtener sesiones del usuario
    sessions = Session.query.filter_by(user_id=user.id).all()
    
    if not sessions:
        return json_response({
            'total_sessions': 0,
            'total_flight_time': 0,
            'total_tricks_landed': 0,
            'avg_motivation': 0,
            'recent_sessions': []
        })
    
    # Calcular estadísticas
    total_sessions = len(sessions)
    total_flight_time = sum(s.flight_duration or 0 for s in sessions)
    total_tricks_landed = sum(s.tricks_landed or 0 for s in sessions)
    
    # Calcular motivación promedio (solo sesiones con datos)
    motivation_sessions = [s for s in sessions if s.motivation_level]
    avg_motivation = sum(s.motivation_level for s in motivation_sessions) / len(motivation_sessions) if motivation_sessions else 0
    
    # Sesiones recientes (últimas 5)
    recent_sessions = sorted(sessions, key=lambda x: x.date, reverse=True)[:5]
    recent_data = []
    
    for session in recent_sessions:
        session_data = {
            'id': session.id,
            'date': session.date,
            'duration': session.duration,
            'flight_duration': session.flight_duration,
            'tricks_landed': session.tricks_landed,
            'motivation_level': session.motivation_level,
            'rating': session.rating
        }
        recent_data.append(session_data)
    
    return json_response({
        'total_sessions': total_sessions,
        'total_flight_time': total_flight_time,
        'total_tricks_landed': total_tricks_landed,
        'avg_motivation': round(avg_motivation, 1),
        'recent_sessions': recent_data
    })
