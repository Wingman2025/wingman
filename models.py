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
    # Feedback fields
    instructor_feedback = db.Column(db.Text)
    student_feedback = db.Column(db.Text)
    # Relationship to session images
    images = db.relationship('SessionImage', backref='session', cascade='all, delete-orphan')
    # Relationship to learning materials
    learning_materials = db.relationship('LearningMaterial', backref='session', lazy='dynamic', cascade='all, delete-orphan')

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

# Goal model: track user-defined goals
class Goal(db.Model):
    __tablename__ = 'goal'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('goals', lazy=True))

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

# Track the status of a skill for a user
class UserSkillStatus(db.Model):
    __tablename__ = 'user_skill_status'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'mastered' or 'in_progress'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('skill_statuses', lazy=True))
    skill = db.relationship('Skill', backref=db.backref('user_statuses', lazy=True))
