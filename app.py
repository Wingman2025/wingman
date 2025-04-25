import os
import sqlite3
import json
import re
from datetime import datetime
import requests
import functools
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, g, render_template, request, redirect, url_for, flash, session, jsonify, Blueprint
from werkzeug.utils import secure_filename
from chatbot import ask_wingfoil_ai
from flask_sqlalchemy import SQLAlchemy
from models import db, SessionImage, Session, User, Skill, Goal, Level
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from uuid import uuid4
from flask_migrate import Migrate
import os

# Create Flask app
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'simple-wingfoil-app-key')
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'wingfoil.db')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'profile_pictures')
app.config['CHAT_IMAGES_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'chat_images')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['S3_KEY'] = 'YOUR_S3_KEY'
app.config['S3_SECRET'] = 'YOUR_S3_SECRET'
app.config['S3_REGION'] = 'YOUR_S3_REGION'
app.config['S3_BUCKET'] = 'YOUR_S3_BUCKET'

# Database URI for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f"sqlite:///{app.config['DATABASE']}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db.init_app(app)
migrate = Migrate(app, db)

# Add Jinja2 filters
def nl2br(value):
    """Convert newlines to <br> tags"""
    if value:
        return value.replace('\n', '<br>')
    return ''

def from_json(value):
    """Convert JSON string to Python object"""
    if value:
        return json.loads(value)
    return {}

app.jinja_env.filters['nl2br'] = nl2br
app.jinja_env.filters['from_json'] = from_json

# S3 upload helper
def upload_file_to_s3(file_obj, bucket, acl="public-read"):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=app.config['S3_KEY'],
        aws_secret_access_key=app.config['S3_SECRET'],
        region_name=app.config.get('S3_REGION')
    )
    filename = secure_filename(f"{uuid4().hex}_{file_obj.filename}")
    try:
        s3.upload_fileobj(
            file_obj,
            bucket,
            filename,
            ExtraArgs={"ACL": acl, "ContentType": file_obj.content_type}
        )
    except (BotoCoreError, ClientError) as e:
        app.logger.error(f"S3 upload failed: {e}")
        return None
    return f"https://{bucket}.s3.{app.config.get('S3_REGION')}.amazonaws.com/{filename}"

# Login required decorator
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('user_id') is None:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

# Blueprint definitions
auth_bp = Blueprint('auth', __name__)
main_bp = Blueprint('main', __name__)
training_bp = Blueprint('training', __name__)
skills_bp = Blueprint('skills', __name__)
levels_bp = Blueprint('levels', __name__)
profile_bp = Blueprint('profile', __name__)
admin_bp = Blueprint('admin', __name__)

# Auth routes
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name', '')
        wingfoil_level_id = request.form.get('wingfoil_level_id') or None
        
        error = None
        
        if not username:
            error = 'Username is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif db.session.query(User).filter_by(username=username).first() is not None:
            error = f"User {username} is already registered."
        elif db.session.query(User).filter_by(email=email).first() is not None:
            error = f"Email {email} is already registered."
            
        if error is None:
            new_user = User(username=username, email=email, password=generate_password_hash(password), name=name, wingfoil_level_id=wingfoil_level_id)
            db.session.add(new_user)
            db.session.commit()
            
            # Iniciar sesión automáticamente
            session.clear()
            session['user_id'] = new_user.id
            session['username'] = new_user.username
            session['name'] = new_user.name
            session['is_admin'] = new_user.is_admin
            
            flash(f'¡Bienvenido a Wingman, {name or username}! Tu cuenta ha sido creada correctamente.', 'success')
            return redirect(url_for('training.stats'))
        
        flash(error, 'danger')
    
    levels = db.session.query(Level).order_by(Level.code).all()
    return render_template('pages/auth/register.html', title='Register', levels=levels)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        error = None
        user = db.session.query(User).filter_by(username=username).first()
        
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'
            
        if error is None:
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username
            session['name'] = user.name
            session['is_admin'] = user.is_admin
            flash(f'Welcome back, {user.name or user.username}!', 'success')
            return redirect(url_for('main.index'))
        
        flash(error, 'danger')
    
    return render_template('pages/auth/login.html', title='Login')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = db.session.query(User).filter_by(id=session['user_id']).first()
    
    if request.method == 'POST':
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file.filename != '':
                if allowed_file(file.filename):
                    # Secure the filename and save the file
                    filename = secure_filename(f"{session['user_id']}_{file.filename}")
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    
                    # Remove old profile picture if it exists
                    if user.profile_picture:
                        old_filepath = os.path.join(app.config['UPLOAD_FOLDER'], user.profile_picture)
                        if os.path.exists(old_filepath):
                            os.remove(old_filepath)
                    
                    # Save new file and update database
                    file.save(filepath)
                    user.profile_picture = filename
                    db.session.commit()
                    flash('Profile picture updated successfully', 'success')
                else:
                    flash('Invalid file type. Allowed types are: png, jpg, jpeg, gif', 'error')
        
        # Handle other profile fields
        if 'update_profile' in request.form:
            nationality = request.form.get('nationality', '')
            age = request.form.get('age', '')
            sports_practiced = request.form.get('sports_practiced', '')
            location = request.form.get('location', '')
            wingfoiling_since = request.form.get('wingfoiling_since', '')
            wingfoil_level_id = request.form.get('wingfoil_level_id', '')
            
            # Convert empty age to NULL
            age = int(age) if age and age.isdigit() else None
            
            # Update the user profile
            user.nationality = nationality
            user.age = age
            user.sports_practiced = sports_practiced
            user.location = location
            user.wingfoiling_since = wingfoiling_since
            user.wingfoil_level_id = wingfoil_level_id
            db.session.commit()
            flash('Profile updated successfully', 'success')
            
        return redirect(url_for('auth.profile'))
    
    session_count = db.session.query(Session).filter_by(user_id=session['user_id']).count()
    levels = db.session.query(Level).order_by(Level.code).all()
    return render_template('pages/auth/profile.html', title='My Profile', 
                       user=user, session_count=session_count, levels=levels)

# Training routes
@training_bp.route('/', methods=['GET'])
@login_required
def stats():
    user_id = session.get('user_id')
    user = db.session.query(User).filter_by(id=user_id).first()
    sessions = db.session.query(Session).filter_by(user_id=user_id).order_by(Session.date.desc()).all()
    goals = db.session.query(Goal).filter_by(user_id=user_id).order_by(Goal.id.desc()).all()
    all_skills = db.session.query(Skill).order_by(Skill.name).all()
    result = render_template('pages/training/stats.html', sessions=sessions, user=user, goals=goals, all_skills=all_skills)
    return result

@training_bp.route('/api/sessions', methods=['GET'])
@login_required
def api_sessions():
    user_id = session.get('user_id')
    sessions_query = db.session.query(Session).filter_by(user_id=user_id).order_by(Session.date.desc()).all()
    sessions_list = []
    for sess in sessions_query:
        sessions_list.append({
            'id': sess.id,
            'date': sess.date,
            'location': sess.location,
            'duration': sess.duration,
            'conditions': sess.conditions,
            'achievements': sess.achievements,
            'challenges': sess.challenges,
            'notes': sess.notes
        })
    return jsonify({'success': True, 'sessions': sessions_list})

@training_bp.route('/log', methods=['GET', 'POST'])
@login_required
def log_session():
    if request.method == 'POST':
        # Process form data
        achievements = request.form.get('achievements', '')
        challenges = request.form.get('challenges', '')
        conditions = request.form.get('conditions', '')
        date = request.form.get('date')
        sport_type = request.form.get('sport_type')
        duration = request.form.get('duration')
        rating = request.form.get('rating')
        location = request.form.get('location')
        notes = request.form.get('notes')
        weather = request.form.get('weather', '')
        wind_speed = request.form.get('wind_speed', '')
        equipment = request.form.get('equipment', '')
        water_conditions = request.form.get('water_conditions', '')
        instructor_feedback = request.form.get('instructor_feedback', '')
        student_feedback = request.form.get('student_feedback', '')
        
        # Process skills
        skills_json = request.form.get('skills', '[]')
        try:
            skills = json.loads(skills_json)
        except json.JSONDecodeError:
            skills = []
        
        skill_ratings = {}
        
        # Validate required fields
        if not date or not sport_type or not duration:
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'success': False, 'error': 'Date, sport type, and duration are required!'})
            flash('Date, sport type, and duration are required!', 'error')
            return redirect(url_for('training.log_session'))
        
        # Save to database
        new_session = Session(
            user_id=session.get('user_id'), date=date,
            sport_type=sport_type, duration=duration,
            rating=rating, location=location, notes=notes,
            skills=json.dumps(skills), skill_ratings=json.dumps(skill_ratings),
            achievements=achievements, challenges=challenges,
            conditions=conditions, weather=weather, wind_speed=wind_speed,
            equipment=equipment, water_conditions=water_conditions,
            instructor_feedback=instructor_feedback, student_feedback=student_feedback
        )
        db.session.add(new_session)
        db.session.commit()
        session_id = new_session.id
        
        # Handle images
        for f in request.files.getlist('images'):
            if f and allowed_file(f.filename):
                url = upload_file_to_s3(f, app.config['S3_BUCKET'])
                if url:
                    img = SessionImage(session_id=session_id, url=url)
                    db.session.add(img)
        db.session.commit()
        
        if request.headers.get('Accept') == 'application/json':
            return jsonify({
                'success': True, 
                'message': 'Training session logged successfully!',
                'session_id': session_id
            })
        
        flash('Training session logged successfully!', 'success')
        return redirect(url_for('training.session_detail', session_id=session_id))
    
    # GET request - show form
    skills = db.session.query(Skill).order_by(Skill.category, Skill.name).all()
    
    # Group skills by category
    skill_categories = {}
    for skill in skills:
        category = skill.category
        if category not in skill_categories:
            skill_categories[category] = []
        skill_categories[category].append(skill)
    
    return render_template('pages/training/log_session.html', skill_categories=skill_categories)

@training_bp.route('/session/<int:session_id>')
@login_required
def session_detail(session_id):
    session_data = db.session.query(Session).filter_by(id=session_id, user_id=session['user_id']).first()
    
    if not session_data:
        flash('Session not found or you do not have permission to view it', 'danger')
        return redirect(url_for('training.stats'))
    
    # Get skills practiced in this session
    practiced_skill_ids = []
    skill_ratings = {}
    
    if session_data.skills:
        try:
            practiced_skill_ids = json.loads(session_data.skills)
            # Convert all IDs to strings for consistent comparison
            practiced_skill_ids = [str(skill_id) for skill_id in practiced_skill_ids]
        except:
            practiced_skill_ids = []
    
    if session_data.skill_ratings:
        try:
            skill_ratings = json.loads(session_data.skill_ratings)
        except:
            skill_ratings = {}
    
    # Initialize skills as an empty list
    skills = []
    
    if practiced_skill_ids and len(practiced_skill_ids) > 0:
        skills_rows = db.session.query(Skill).filter(Skill.id.in_(practiced_skill_ids)).all()
        
        # Convert to list of dicts
        for skill_row in skills_rows:
            skill = skill_row.__dict__
            skill_id = str(skill['id'])
            if skill_id in skill_ratings:
                skill['rating'] = skill_ratings[skill_id]
            skills.append(skill)
    
    # Get all skills for the edit form
    all_skills = db.session.query(Skill).order_by(Skill.category, Skill.name).all()
    
    # Group skills by category for the form
    skill_categories = {}
    for skill in all_skills:
        category = skill.category
        if category not in skill_categories:
            skill_categories[category] = []
        skill_categories[category].append(skill.__dict__)
    
    # Convert session_data to a dictionary
    session_dict = session_data.__dict__
    
    return render_template('pages/training/session_detail.html', 
                          title='Session Details', 
                          session=session_dict, 
                          skills=skills,
                          skill_categories=skill_categories,
                          practiced_skill_ids=practiced_skill_ids,
                          skill_ratings=skill_ratings)

@training_bp.route('/session/update', methods=['POST'])
@login_required
def update_session():
    session_id = request.form.get('session_id')
    date = request.form.get('date')
    sport_type = request.form.get('sport_type')
    duration = request.form.get('duration')
    rating = request.form.get('rating')
    location = request.form.get('location', '')
    notes = request.form.get('notes', '')
    achievements = request.form.get('achievements', '')
    challenges = request.form.get('challenges', '')
    conditions = request.form.get('conditions', '')
    weather = request.form.get('weather', '')
    wind_speed = request.form.get('wind_speed', '')
    equipment = request.form.get('equipment', '')
    water_conditions = request.form.get('water_conditions', '')
    instructor_feedback = request.form.get('instructor_feedback', '')
    student_feedback = request.form.get('student_feedback', '')
    
    # Get skills and skill ratings
    skills = request.form.getlist('skills')
    skill_ratings = request.form.get('skill_ratings', '{}')
    
    # Validate required fields
    if not all([session_id, date, sport_type, duration]):
        flash('Please fill in all required fields', 'danger')
        return redirect(url_for('training.session_detail', session_id=session_id))
    
    session_data = db.session.query(Session).filter_by(id=session_id, user_id=session['user_id']).first()
    
    if not session_data:
        flash('Session not found or you do not have permission to edit it', 'danger')
        return redirect(url_for('training.stats'))
    
    # Update session in database
    session_data.date = date
    session_data.sport_type = sport_type
    session_data.duration = duration
    session_data.rating = rating
    session_data.location = location
    session_data.notes = notes
    session_data.skills = json.dumps(skills)
    session_data.skill_ratings = skill_ratings
    session_data.achievements = achievements
    session_data.challenges = challenges
    session_data.conditions = conditions
    session_data.weather = weather
    session_data.wind_speed = wind_speed
    session_data.equipment = equipment
    session_data.water_conditions = water_conditions
    session_data.instructor_feedback = instructor_feedback
    session_data.student_feedback = student_feedback
    db.session.commit()
    flash('Session updated successfully', 'success')
    return redirect(url_for('training.session_detail', session_id=session_id))

# Route to add a new goal
@training_bp.route('/goals/add', methods=['POST'])
@login_required
def add_goal():
    user_id = session.get('user_id')
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    skill_id = request.form.get('skill_id') or None
    target_date_str = request.form.get('target_date')
    target_date = datetime.strptime(target_date_str, '%Y-%m-%d') if target_date_str else None
    new_goal = Goal(user_id=user_id, title=title, description=description, skill_id=skill_id, target_date=target_date)
    db.session.add(new_goal)
    db.session.commit()
    flash('Goal added successfully', 'success')
    return redirect(url_for('training.stats'))

# Route to update a goal
@training_bp.route('/goals/update', methods=['POST'])
@login_required
def update_goal():
    goal_id = request.form.get('goal_id')
    goal = db.session.query(Goal).get(goal_id)
    goal.title = request.form.get('title', '').strip()
    goal.description = request.form.get('description', '').strip()
    skill_id = request.form.get('skill_id') or None
    goal.skill_id = skill_id
    target_date_str = request.form.get('target_date')
    if target_date_str:
        goal.target_date = datetime.strptime(target_date_str, '%Y-%m-%d')
    db.session.commit()
    flash('Goal updated successfully', 'success')
    return redirect(url_for('training.stats'))

# Skills routes
@skills_bp.route('/', methods=['GET'])
@login_required
def skills_index():
    skills = db.session.query(Skill).order_by(Skill.name).all()
    return render_template('pages/skills/index.html', skills=skills)

# Levels routes
@levels_bp.route('/', methods=['GET'])
@login_required
def levels_index():
    return render_template('pages/levels/index.html')

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
@main_bp.route('/')
def index():
    # Render a custom homepage instead of redirecting
    return render_template('pages/main/index.html', title='Home')
app.register_blueprint(main_bp)
app.register_blueprint(training_bp, url_prefix='/training')
app.register_blueprint(skills_bp, url_prefix='/skills')
app.register_blueprint(levels_bp, url_prefix='/levels')
app.register_blueprint(profile_bp, url_prefix='/profile')

@admin_bp.route('/login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        error = None
        user = db.session.query(User).filter_by(username=username).first()
        if user is None or not user.is_admin or not check_password_hash(user.password, password):
            error = 'Invalid admin credentials'
        if error:
            flash(error, 'danger')
            return redirect(url_for('admin.admin_login'))
        session.clear()
        session['user_id'] = user.id
        session['username'] = user.username
        session['name'] = user.name
        session['is_admin'] = True
        flash('Successfully logged in as admin', 'success')
        return redirect(url_for('admin.admin_index'))
    return render_template('pages/admin/login.html')

@admin_bp.route('/')
@login_required
def admin_index():
    if not session.get('is_admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    if not session.get('is_admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    users = db.session.query(User).all()
    users_data = []
    for u in users:
        sess_list = db.session.query(Session).filter_by(user_id=u.id).all()
        total_sessions = len(sess_list)
        instr_comments = sum(1 for s in sess_list if s.instructor_feedback)
        stud_comments = sum(1 for s in sess_list if s.student_feedback)
        users_data.append({'user': u, 'total_sessions': total_sessions, 'instructor_comments': instr_comments, 'student_comments': stud_comments})
    return render_template('pages/admin/dashboard.html', users_data=users_data)

@admin_bp.route('/sessions')
@login_required
def admin_sessions():
    if not session.get('is_admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    sessions = db.session.query(Session).all()
    return render_template('pages/admin/sessions.html', sessions=sessions)

@admin_bp.route('/session/<int:session_id>', methods=['GET','POST'])
@login_required
def admin_session_detail(session_id):
    if not session.get('is_admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    sess = db.session.query(Session).filter_by(id=session_id).first()
    if not sess:
        flash('Session not found.', 'danger')
        return redirect(url_for('admin.admin_sessions'))
    if request.method == 'POST':
        instr = request.form.get('instructor_feedback', '')
        stud = request.form.get('student_feedback', '')
        sess.instructor_feedback = instr
        sess.student_feedback = stud
        db.session.commit()
        flash('Feedback updated.', 'success')
        return redirect(url_for('admin.admin_session_detail', session_id=session_id))
    return render_template('pages/admin/session_detail.html', session=sess)

app.register_blueprint(admin_bp, url_prefix='/admin')

# Ensure upload directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CHAT_IMAGES_FOLDER'], exist_ok=True)

# Chatbot API route
@app.route('/api/chat', methods=['POST'])
def chat_api():
    # Check if the request is form data or JSON
    if request.is_json:
        data = request.get_json()
        question = data.get('question', '') or data.get('message', '')
    else:
        # Handle form data
        question = request.form.get('message', '') or request.form.get('question', '')
    
    if not question:
        return jsonify({'error': 'No question or message provided'}), 400
    
    try:
        response = ask_wingfoil_ai(question)
        return jsonify({'response': response})
    except Exception as e:
        app.logger.error(f"Error in chat_api: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Chatbot with image API route
@app.route('/api/chat_with_image', methods=['POST'])
def chat_with_image_api():
    question = request.form.get('question', '')
    image = request.files.get('image')
    
    if not image:
        return jsonify({'error': 'No image provided'}), 400
    
    try:
        # Save the image
        filename = secure_filename(image.filename)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        image_path = os.path.join(app.config['CHAT_IMAGES_FOLDER'], unique_filename)
        image.save(image_path)
        
        # Get response from AI with image
        response = ask_wingfoil_ai(question, image_path)
        
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.teardown_appcontext
def close_db_connection(exception):
    db.session.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Utility functions for wsgi entrypoint
def initialize_database():
    """Run database migrations to set up the schema."""
    from flask_migrate import upgrade
    upgrade()

def get_db():
    """Return a database connection for wsgi health checks."""
    return db.session.get_bind().connect()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5010)
