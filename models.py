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
    profile_picture = db.Column(db.String(200))
    nationality = db.Column(db.String(100))
    age = db.Column(db.Integer)
    sports_practiced = db.Column(db.String)
    location = db.Column(db.String)
    wingfoiling_since = db.Column(db.String)
    wingfoil_level = db.Column(db.String)
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
    # Relationship to session images
    images = db.relationship('SessionImage', backref='session', cascade='all, delete-orphan')

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
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
