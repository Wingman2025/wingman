from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
# To be initialized with app in app.py

# Create db instance
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100))
    profile_picture = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    nationality = db.Column(db.String(100))
    age = db.Column(db.Integer)
    sports_practiced = db.Column(db.String)
    location = db.Column(db.String)
    wingfoiling_since = db.Column(db.String)
    wingfoil_level = db.Column(db.String)
    # Link to levels table
    wingfoil_level_id = db.Column(db.Integer, db.ForeignKey('level.id'), nullable=True)
    level = db.relationship('Level', backref=db.backref('users', lazy=True))
    # One user has many sessions
    sessions = db.relationship('Session', backref='user', cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Session(db.Model):
    __tablename__ = 'session'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.String, nullable=False)
    sport_type = db.Column(db.String, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer)
    location = db.Column(db.String)
    notes = db.Column(db.Text)
    skills = db.Column(db.Text)
    skill_ratings = db.Column(db.Text)
    achievements = db.Column(db.Text)
    challenges = db.Column(db.Text)
    conditions = db.Column(db.Text)
    weather = db.Column(db.Text)
    wind_speed = db.Column(db.Text)
    equipment = db.Column(db.Text)
    water_conditions = db.Column(db.Text)
    instructor_feedback = db.Column(db.Text)
    student_feedback = db.Column(db.Text)
    # Relationship to session images
    images = db.relationship('SessionImage', backref='session', cascade='all, delete-orphan')
    # Relationship to learning materials
    learning_materials = db.relationship('LearningMaterial', backref='session', lazy='dynamic', cascade='all, delete-orphan')
    
    # Companion App Motivacional - Campos extendidos para tracking detallado
    flight_duration = db.Column(db.Integer)  # duración de vuelo en minutos
    upwind_distance = db.Column(db.Float)  # distancia contra viento en metros
    falls_count = db.Column(db.Integer, default=0)  # número de caídas
    max_speed = db.Column(db.Float)  # velocidad máxima alcanzada en km/h
    avg_speed = db.Column(db.Float)  # velocidad promedio en km/h
    tricks_attempted = db.Column(db.Integer, default=0)  # trucos intentados
    tricks_landed = db.Column(db.Integer, default=0)  # trucos conseguidos
    water_time = db.Column(db.Integer)  # tiempo total en el agua en minutos
    preparation_time = db.Column('preparation_time', db.Integer)  # tiempo de preparación en minutos
    session_type = db.Column(db.String(50))  # 'training', 'freeride', 'competition', etc.
    motivation_level = db.Column(db.Integer)  # nivel de motivación 1-10
    energy_level_before = db.Column(db.Integer)  # energía antes 1-10
    energy_level_after = db.Column(db.Integer)  # energía después 1-10
    goals_worked_on = db.Column(db.Text)  # objetivos en los que se trabajó (JSON)
    personal_bests = db.Column(db.Text)  # récords personales alcanzados (JSON)

class SessionImage(db.Model):
    __tablename__ = 'session_image'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    url = db.Column(db.String, nullable=False)

# Skill model
class Skill(db.Model):
    __tablename__ = 'skill'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Track a user's progress on each skill
class UserSkillStatus(db.Model):
    __tablename__ = 'user_skill_status'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'mastered' or 'in_progress'
    user = db.relationship('User', backref=db.backref('skill_statuses', lazy=True))
    skill = db.relationship('Skill', backref=db.backref('user_statuses', lazy=True))

# Goal Template model: plantillas de objetivos predefinidos
class GoalTemplate(db.Model):
    __tablename__ = 'goal_template'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)  # 'technique', 'endurance', 'progression', etc.
    difficulty_level = db.Column(db.String(20), nullable=False)  # 'beginner', 'intermediate', 'advanced'
    estimated_duration_days = db.Column(db.Integer)  # duración estimada en días
    icon = db.Column(db.String(50))  # nombre del icono para UI
    target_type = db.Column(db.String(20), nullable=False)  # 'count', 'duration', 'distance', 'boolean'
    default_target_value = db.Column(db.Integer)  # valor objetivo por defecto
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# User Goal model: objetivos activos por usuario
class UserGoal(db.Model):
    __tablename__ = 'user_goal'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    goal_template_id = db.Column(db.Integer, db.ForeignKey('goal_template.id'), nullable=True)
    custom_title = db.Column(db.String(200))  # título personalizado si no usa template
    custom_description = db.Column(db.Text)  # descripción personalizada
    target_value = db.Column(db.Integer, nullable=False)  # valor objetivo (ej: 10 jibes, 60 minutos)
    current_progress = db.Column(db.Integer, default=0)  # progreso actual
    status = db.Column(db.String(20), default='active')  # 'active', 'completed', 'paused', 'abandoned'
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    target_date = db.Column(db.DateTime)
    completed_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('user_goals', lazy=True))
    goal_template = db.relationship('GoalTemplate', backref=db.backref('user_goals', lazy=True))

# Badge model: sistema de logros/medallas
class Badge(db.Model):
    __tablename__ = 'badge'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50))  # nombre del icono
    category = db.Column(db.String(50), nullable=False)  # 'progression', 'consistency', 'achievement', etc.
    criteria = db.Column(db.Text)  # criterios para desbloquear (JSON o texto)
    points_value = db.Column(db.Integer, default=10)  # puntos que otorga el badge
    rarity = db.Column(db.String(20), default='common')  # 'common', 'rare', 'epic', 'legendary'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# User Badge model: badges desbloqueados por usuario
class UserBadge(db.Model):
    __tablename__ = 'user_badge'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badge.id'), nullable=False)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)
    progress_when_unlocked = db.Column(db.Text)  # contexto del progreso cuando se desbloqueó
    
    # Relationships
    user = db.relationship('User', backref=db.backref('user_badges', lazy=True))
    badge = db.relationship('Badge', backref=db.backref('user_badges', lazy=True))
    
    # Unique constraint: un usuario no puede tener el mismo badge dos veces
    __table_args__ = (db.UniqueConstraint('user_id', 'badge_id', name='unique_user_badge'),)

# Level model: track wingfoil progression
class Level(db.Model):
    __tablename__ = 'level'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Learning Material model for YouTube links
class LearningMaterial(db.Model):
    __tablename__ = 'learning_material'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    url = db.Column(db.String, nullable=False) # YouTube URL
    title = db.Column(db.String) # Extracted title
    thumbnail_url = db.Column(db.String) # Extracted thumbnail
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Product (Gear) model for sport equipment
class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationship: one product has many images
    images = db.relationship('ProductImage', backref='product', cascade='all, delete-orphan', lazy=True)

# Product Image model
class ProductImage(db.Model):
    __tablename__ = 'product_image'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    image_url = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Chat history model
class ChatMessage(db.Model):
    __tablename__ = 'chat_message'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role = db.Column(db.String(10), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.String(36), nullable=True)  # UUID for conversation session
    user = db.relationship('User', backref=db.backref('chat_messages', lazy='dynamic'))

# Chat message helper functions
def insert_message(session_id, sender, message, user_id=None):
    """Insert a new message into the chat history."""
    chat_msg = ChatMessage(
        user_id=user_id,
        role=sender,  # 'user' or 'assistant'
        content=message,
        session_id=session_id
    )
    db.session.add(chat_msg)
    db.session.commit()
    return chat_msg


def fetch_history(session_id):
    """Fetch complete conversation history for a session, ordered by time."""
    messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.timestamp.asc()).all()
    return [
        {
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
        }
        for msg in messages
    ]


def format_history_for_context(session_id, max_messages=10):
    """Format conversation history as context string for the AI agent.
    
    Args:
        session_id: The session ID to fetch history for
        max_messages: Maximum number of recent messages to include (default: 10)
    """
    history = fetch_history(session_id)
    if not history:
        return ""
    
    # Limitar a los últimos N mensajes para optimizar tokens
    recent_history = history[-max_messages:] if len(history) > max_messages else history
    
    context_lines = []
    for msg in recent_history:
        # Truncar mensajes muy largos para optimizar tokens
        content = msg['content']
        if len(content) > 200:
            content = content[:200] + "..."
        context_lines.append(f"{msg['role']}: {content}")
    
    return "\n".join(context_lines)
