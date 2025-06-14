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
# from chatbot import ask_wingfoil_ai # Old chatbot
from agent import agent_bp # New agent-based chatbot
from models import db, SessionImage, Session, User, Skill, Goal, Level, LearningMaterial, Product, ProductImage, UserSkillStatus
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from uuid import uuid4
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
load_dotenv()

# Create Flask app
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'simple-wingfoil-app-key')
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'wingfoil.db')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'profile_pictures')
app.config['CHAT_IMAGES_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'chat_images')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'webm'}
app.config['S3_KEY']    = os.environ.get('S3_KEY')    # AWS Access Key ID
app.config['S3_SECRET'] = os.environ.get('S3_SECRET') # AWS Secret Access Key
app.config['S3_REGION'] = os.environ.get('S3_REGION') # AWS Region
app.config['S3_BUCKET'] = os.environ.get('S3_BUCKET') # S3 Bucket Name

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
def upload_file_to_s3(file_obj, bucket):
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
            ExtraArgs={"ContentType": file_obj.content_type}
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
community_bp = Blueprint('community', __name__) # Added Community Blueprint

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

@profile_bp.route('/', methods=['GET', 'POST'])
@login_required
def profile():
    user = db.session.query(User).filter_by(id=session['user_id']).first()
    
    if request.method == 'POST':
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename:
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[-1].lower()
                if ext not in app.config['ALLOWED_EXTENSIONS']:
                    flash('Invalid image file type.', 'danger')
                    return redirect(url_for('profile.profile'))
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(upload_path)
                # Remove old profile picture if it exists
                if user.profile_picture:
                    old_filepath = os.path.join(app.config['UPLOAD_FOLDER'], user.profile_picture)
                    if os.path.exists(old_filepath):
                        os.remove(old_filepath)
                user.profile_picture = filename
                db.session.commit()
                flash('Profile picture updated successfully', 'success')
                return redirect(url_for('profile.profile'))
        # Handle other profile fields
        if 'update_profile' in request.form:
            name = request.form.get('name')
            email = request.form.get('email')
            nationality = request.form.get('nationality')
            age = request.form.get('age')
            sports_practiced = request.form.get('sports_practiced')
            location = request.form.get('location')
            wingfoiling_since = request.form.get('wingfoiling_since')
            wingfoil_level_id = request.form.get('wingfoil_level_id') or None
            # Update the user profile
            user.name = name or user.name
            user.email = email or user.email
            user.nationality = nationality
            user.age = age
            user.sports_practiced = sports_practiced
            user.location = location
            user.wingfoiling_since = wingfoiling_since
            user.wingfoil_level_id = wingfoil_level_id
            db.session.commit()
            flash('Profile updated successfully', 'success')
            return redirect(url_for('profile.profile'))
    session_count = db.session.query(Session).filter_by(user_id=session['user_id']).count()
    levels = db.session.query(Level).order_by(Level.code).all()
    return render_template('pages/auth/profile.html', title='My Profile', user=user, session_count=session_count, levels=levels)

# Training routes
@training_bp.route('/', methods=['GET'])
@login_required
def stats():
    user_id = session.get('user_id')
    user = db.session.query(User).filter_by(id=user_id).first()
    sessions = db.session.query(Session).filter_by(user_id=user_id).order_by(Session.date.desc()).all()
    goals = db.session.query(Goal).filter_by(user_id=user_id).order_by(Goal.id.desc()).all()
    mastered_skills = db.session.query(UserSkillStatus).filter_by(user_id=user_id, status='mastered').all()
    inprogress_skills = db.session.query(UserSkillStatus).filter_by(user_id=user_id, status='in_progress').all()
    result = render_template(
        'pages/training/stats.html',
        sessions=sessions,
        user=user,
        goals=goals,
        mastered_skills=mastered_skills,
        inprogress_skills=inprogress_skills
    )
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
        
        # Depuración: loggear archivos recibidos
        print('Archivos recibidos:', request.files)
        print('Lista de imágenes:', request.files.getlist('images'))
        # Handle images
        for f in request.files.getlist('images'):
            print('Procesando archivo:', f.filename)
            if f and allowed_file(f.filename):
                url = upload_file_to_s3(f, app.config['S3_BUCKET'])
                print('URL subida:', url)
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

from sqlalchemy.orm import joinedload

@training_bp.route('/session/<int:session_id>')
@login_required
def session_detail(session_id):
    session_data = db.session.query(Session).options(
        joinedload(Session.images),
        joinedload(Session.learning_materials)
    ).filter_by(id=session_id, user_id=session['user_id']).first()
    
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
    
    return render_template('pages/training/session_detail.html', 
                          title='Session Details', 
                          session=session_data, 
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

    # Handle image uploads
    if 'images' in request.files:
        for f in request.files.getlist('images'):
            if f and f.filename != '' and allowed_file(f.filename):
                try:
                    url = upload_file_to_s3(f, app.config['S3_BUCKET'])
                    if url:
                        db.session.add(SessionImage(session_id=session_data.id, url=url))
                    else:
                        flash(f'Failed to upload {f.filename}.', 'warning')
                except Exception as e:
                    app.logger.error(f"Error uploading file {f.filename}: {e}")
                    flash(f'An error occurred while uploading {f.filename}.', 'danger')
            elif f and f.filename != '':
                flash(f'File type not allowed for {f.filename}.', 'warning')

    # Handle new Learning Material (YouTube link)
    new_youtube_url = request.form.get('new_learning_material_url')
    if new_youtube_url:
        if 'youtube.com/watch?v=' in new_youtube_url or 'youtu.be/' in new_youtube_url:
            try:
                oembed_url = f"https://www.youtube.com/oembed?url={new_youtube_url}&format=json"
                response = requests.get(oembed_url)
                response.raise_for_status()
                data = response.json()
                title = data.get('title')
                thumbnail_url = data.get('thumbnail_url')
                if title and thumbnail_url:
                    db.session.add(LearningMaterial(session_id=session_data.id, url=new_youtube_url, title=title, thumbnail_url=thumbnail_url))
                else:
                    flash('Could not fetch YouTube video details.', 'warning')
            except requests.exceptions.RequestException as e:
                app.logger.error(f"Error fetching YouTube oEmbed for {new_youtube_url}: {e}")
                flash('Error fetching YouTube video details. Please check the URL.', 'danger')
            except Exception as e:
                app.logger.error(f"Error processing YouTube link {new_youtube_url}: {e}")
                flash('An unexpected error occurred while adding the YouTube link.', 'danger')
        else:
            flash('Invalid YouTube URL provided.', 'warning')

    try:
        db.session.commit()
        flash('Session updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating session {session_id}: {e}")
        flash('Failed to update session. Please try again.', 'danger')
    return redirect(url_for('training.session_detail', session_id=session_id))

# Route to add a new goal
@training_bp.route('/goals/add', methods=['POST'])
@login_required
def add_goal():
    user_id = session.get('user_id')
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    target_date_str = request.form.get('target_date')
    target_date = datetime.strptime(target_date_str, '%Y-%m-%d') if target_date_str else None
    new_goal = Goal(user_id=user_id, title=title, description=description,
                    target_date=target_date)
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
    target_date_str = request.form.get('target_date')
    if target_date_str:
        goal.target_date = datetime.strptime(target_date_str, '%Y-%m-%d')
    progress_val = request.form.get('progress')
    if progress_val is not None:
        try:
            goal.progress = int(progress_val)
        except ValueError:
            app.logger.warning(f"Invalid progress value: {progress_val}")
    db.session.commit()
    flash('Goal updated successfully', 'success')
    return redirect(url_for('training.stats'))

# Update user skill status
@training_bp.route('/skills/update_status', methods=['POST'])
@login_required
def update_skill_status():
    skill_id = request.form.get('skill_id')
    new_status = request.form.get('new_status')
    user_id = session.get('user_id')

    status_entry = db.session.query(UserSkillStatus).filter_by(user_id=user_id, skill_id=skill_id).first()
    if status_entry:
        status_entry.status = new_status
    else:
        status_entry = UserSkillStatus(user_id=user_id, skill_id=skill_id, status=new_status)
        db.session.add(status_entry)
    db.session.commit()
    flash('Skill status updated', 'success')
    return redirect(url_for('training.stats'))

# Skills routes
@skills_bp.route('/', methods=['GET'])
@login_required
def skills_index():
    # Static roadmap page showing full content; DB-based skill selection remains in log_session
    return render_template('skills/index.html')

# Levels routes
@levels_bp.route('/', methods=['GET'])
@login_required
def levels_index():
    return render_template('pages/levels/index.html')

# Gear page route
@main_bp.route('/gear')
def gear():
    products = db.session.query(Product).filter_by(is_available=True).order_by(Product.created_at.desc()).all()
    return render_template('pages/gear.html', title='Gear', products=products)

# Community routes
@community_bp.route('/')
def index():
    return render_template('community/index.html', title='Community')

# Home page route
@main_bp.route('/')
def index():
    # Fetch Tarifa weather via Met.no free API
    lat, lon = 36.0111, -5.6077
    
    # Define a mapping from Met.no symbol codes to Bootstrap Icons
    # (Add more mappings as needed based on https://api.met.no/weatherapi/weathericon/2.0/documentation)
    symbol_to_icon = {
        'clearsky_day': 'bi-sun-fill',
        'clearsky_night': 'bi-moon-stars-fill',
        'fair_day': 'bi-cloud-sun-fill',
        'fair_night': 'bi-cloud-moon-fill',
        'partlycloudy_day': 'bi-cloud-sun-fill',
        'partlycloudy_night': 'bi-cloud-moon-fill',
        'cloudy': 'bi-cloud-fill',
        'rain': 'bi-cloud-rain-fill',
        'lightrain': 'bi-cloud-drizzle-fill',
        'heavyrain': 'bi-cloud-rain-heavy-fill',
        'sleet': 'bi-cloud-sleet-fill',
        'snow': 'bi-cloud-snow-fill',
        'fog': 'bi-cloud-fog2-fill',
        # Add more complex conditions if desired
        'rainshowers_day': 'bi-cloud-rain-fill',
        'rainshowers_night': 'bi-cloud-rain-fill',
        'snowshowers_day': 'bi-cloud-snow-fill',
        'snowshowers_night': 'bi-cloud-snow-fill',
    }
    default_icon = 'bi-thermometer-half' # Fallback icon

    # Default weather fallback
    weather = {
        'current': {'icon': default_icon, 'temp': '--', 'description': 'Unavailable'},
        'wind':    {'icon': 'bi-wind',  'speed': '--', 'direction': '--'},
        'water':   {'icon': 'bi-water', 'temp': '--', 'wave_height': '--'}
    }
    try:
        headers = {'User-Agent': 'WingmanApp/1.0 (contact@wingman.example)'}
        resp = requests.get(
            'https://api.met.no/weatherapi/locationforecast/2.0/compact',
            params={'lat': lat, 'lon': lon}, headers=headers, timeout=5
        )
        data = resp.json()
        times = data.get('properties', {}).get('timeseries', [])
        if times:
            inst = times[0]['data']['instant']['details']
            next_hour_summary = times[0]['data'].get('next_1_hours', {}).get('summary', {})
            symbol_code = next_hour_summary.get('symbol_code')
            
            # Determine description and icon
            # Simplified description for now, could map symbol_code to text later
            description = symbol_code.replace('_', ' ').capitalize() if symbol_code else 'Current Conditions'
            icon_class = symbol_to_icon.get(symbol_code, default_icon)
            
            temp = round(inst.get('air_temperature', 0))
            ws = round(inst.get('wind_speed', 0) * 3.6)
            wd = round(inst.get('wind_from_direction', 0))
            weather = {
                'current': {'icon': icon_class, 'temp': temp, 'description': description},
                'wind':    {'icon': 'bi-wind', 'speed': ws, 'direction': f"{wd}°"},
                'water':   {'icon': 'bi-water', 'temp': '--', 'wave_height': '--'}
            }
    except Exception as e:
        app.logger.error(f"Weather fetch error: {e}")
    current_time = datetime.now().strftime('%H:%M')
    # Fetch up to 4 available products for the home page
    featured_products = Product.query.filter_by(is_available=True).order_by(Product.created_at.desc()).limit(4).all()
    return render_template(
        'pages/index_updated.html', title='Home',
        weather=weather, current_time=current_time,
        featured_products=featured_products
    )
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(main_bp)
app.register_blueprint(training_bp, url_prefix='/training')
app.register_blueprint(skills_bp, url_prefix='/skills')
app.register_blueprint(levels_bp, url_prefix='/levels')
app.register_blueprint(profile_bp, url_prefix='/profile')
app.register_blueprint(agent_bp) # Registering the new agent blueprint
app.register_blueprint(community_bp, url_prefix='/community') # Registered Community Blueprint

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

@admin_bp.route('/sessions', defaults={'user_id': None})
@admin_bp.route('/sessions/user/<int:user_id>')
@login_required
def admin_sessions(user_id):
    if not session.get('is_admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    if user_id:
        sessions = db.session.query(Session).filter_by(user_id=user_id).all()
    else:
        sessions = db.session.query(Session).all()
    return render_template('pages/admin/sessions.html', sessions=sessions)

from sqlalchemy.orm import joinedload

@admin_bp.route('/session/<int:session_id>', methods=['GET', 'POST'])
@login_required
def admin_session_detail(session_id):
    # Ensure user is admin
    if not session.get('is_admin'):
        flash('Access denied: Admins only.', 'danger')
        return redirect(url_for('main.index'))

    session_data = db.session.query(Session).options(
        db.joinedload(Session.user),
        db.joinedload(Session.images),
        db.joinedload(Session.learning_materials) # Load learning materials
    ).get(session_id)

    if not session_data:
        flash('Session not found.', 'danger')
        return redirect(url_for('admin.dashboard')) # Or wherever admin sessions are listed

    if request.method == 'POST':
        # Update session fields from form data
        session_data.achievements = request.form.get('achievements', session_data.achievements)
        session_data.challenges = request.form.get('challenges', session_data.challenges)
        session_data.conditions = request.form.get('conditions', session_data.conditions)
        session_data.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date() if request.form.get('date') else session_data.date
        session_data.sport_type = request.form.get('sport_type', session_data.sport_type)
        session_data.duration = int(request.form.get('duration')) if request.form.get('duration') else session_data.duration
        session_data.rating = int(request.form.get('rating')) if request.form.get('rating') else session_data.rating
        session_data.location = request.form.get('location', session_data.location)
        session_data.notes = request.form.get('notes', session_data.notes)

        # Handle image uploads
        if 'images' in request.files:
            for f in request.files.getlist('images'):
                if f and f.filename != '' and allowed_file(f.filename):
                    try:
                        url = upload_file_to_s3(f, app.config['S3_BUCKET'])
                        if url:
                            new_image = SessionImage(session_id=session_data.id, url=url)
                            db.session.add(new_image)
                        else:
                            flash(f'Failed to upload {f.filename}.', 'warning')
                    except Exception as e:
                        app.logger.error(f"Error uploading file {f.filename}: {e}")
                        flash(f'An error occurred while uploading {f.filename}.', 'danger')
                elif f and f.filename != '': # File exists but is not allowed
                    flash(f'File type not allowed for {f.filename}.', 'warning')

        # Handle new Learning Material (YouTube link)
        new_youtube_url = request.form.get('new_learning_material_url')
        if new_youtube_url:
            # Basic validation (could be more robust)
            if 'youtube.com/watch?v=' in new_youtube_url or 'youtu.be/' in new_youtube_url:
                try:
                    # Use YouTube oEmbed to get title and thumbnail
                    oembed_url = f"https://www.youtube.com/oembed?url={new_youtube_url}&format=json"
                    response = requests.get(oembed_url)
                    response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                    data = response.json()
                    title = data.get('title')
                    thumbnail_url = data.get('thumbnail_url')

                    if title and thumbnail_url:
                        new_material = LearningMaterial(
                            session_id=session_data.id,
                            url=new_youtube_url,
                            title=title,
                            thumbnail_url=thumbnail_url
                        )
                        db.session.add(new_material)
                    else:
                        flash('Could not fetch YouTube video details.', 'warning')
                except requests.exceptions.RequestException as e:
                    app.logger.error(f"Error fetching YouTube oEmbed for {new_youtube_url}: {e}")
                    flash('Error fetching YouTube video details. Please check the URL.', 'danger')
                except Exception as e:
                    app.logger.error(f"Error processing YouTube link {new_youtube_url}: {e}")
                    flash('An unexpected error occurred while adding the YouTube link.', 'danger')
            else:
                flash('Invalid YouTube URL provided.', 'warning')

        # Note: Handling updates/deletions for skills and goals would require more complex logic here.
        # Focusing on core session details and image uploads for now.

        try:
            db.session.commit()
            flash('Session updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error updating session {session_id}: {e}")
            flash('Failed to update session. Please try again.', 'danger')

        return redirect(url_for('admin.admin_session_detail', session_id=session_id))

    # GET request - Prepare data for the template (existing logic)
    session_skills_data = {}
    practiced_skill_ids = []
    skill_ratings = {}
    if session_data.skills:
        try:
            practiced_skill_ids = json.loads(session_data.skills)
            practiced_skill_ids = [str(skill_id) for skill_id in practiced_skill_ids]
        except:
            practiced_skill_ids = []
    if session_data.skill_ratings:
        try:
            skill_ratings = json.loads(session_data.skill_ratings)
        except:
            skill_ratings = {}
    skills = []
    if practiced_skill_ids:
        skills_rows = db.session.query(Skill).filter(Skill.id.in_(practiced_skill_ids)).all()
        for skill_row in skills_rows:
            skill = skill_row.__dict__
            skill_id = str(skill['id'])
            if skill_id in skill_ratings:
                skill['rating'] = skill_ratings[skill_id]
            skills.append(skill)
    all_skills = db.session.query(Skill).order_by(Skill.category, Skill.name).all()
    skill_categories = {}
    for skill in all_skills:
        category = skill.category
        skill_categories.setdefault(category, []).append(skill.__dict__)
    goals = db.session.query(Goal).filter_by(user_id=session_data.user_id).order_by(Goal.id.desc()).all()
    goals_data = [goal.__dict__ for goal in goals]
    return render_template('pages/training/session_detail.html', 
                          title=f"Admin Edit: Session {session_id}", 
                          session=session_data, 
                          skills=skills,
                          skill_categories=skill_categories,
                          practiced_skill_ids=practiced_skill_ids,
                          skill_ratings=skill_ratings,
                          goals=goals_data,
                          config=app.config) # Pass config to template

# --- Admin Product Management ---
from flask import abort

@admin_bp.route('/products')
@login_required
def products():
    if not session.get('is_admin'):
        abort(403)
    products = db.session.query(Product).order_by(Product.created_at.desc()).all()
    return render_template('pages/admin/products.html', products=products)

@admin_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if not session.get('is_admin'):
        abort(403)
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image_url = request.form['image_url']
        is_available = request.form.get('is_available', '1') == '1'
        # Handle main image file upload
        file = request.files.get('image_file')
        if file and file.filename:
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[-1].lower()
            if ext not in app.config['ALLOWED_EXTENSIONS']:
                flash('Invalid image file type.', 'danger')
                return render_template('pages/admin/product_form.html', product=None)
            is_production = os.environ.get('FLASK_ENV') == 'production' or os.environ.get('RAILWAY_STATIC_URL') or os.environ.get('RAILWAY_ENVIRONMENT')
            if is_production and app.config.get('S3_BUCKET'):
                s3_url = upload_file_to_s3(file, app.config['S3_BUCKET'])
                if not s3_url:
                    flash('Failed to upload image to S3.', 'danger')
                    return render_template('pages/admin/product_form.html', product=None)
                image_url = s3_url
            else:
                upload_path = os.path.join(app.root_path, 'static', 'uploads', filename)
                file.save(upload_path)
                image_url = url_for('static', filename=f'uploads/{filename}')
        product = Product(name=name, description=description, price=price, image_url=image_url, is_available=is_available)
        db.session.add(product)
        db.session.commit()
        # Handle multiple extra images
        extra_images = request.files.getlist('extra_images')
        for extra_file in extra_images:
            if extra_file and extra_file.filename:
                ext = extra_file.filename.rsplit('.', 1)[-1].lower()
                if ext not in app.config['ALLOWED_EXTENSIONS']:
                    flash(f'Archivo de imagen adicional inválido: {extra_file.filename}', 'danger')
                    continue
                if is_production and app.config.get('S3_BUCKET'):
                    s3_url = upload_file_to_s3(extra_file, app.config['S3_BUCKET'])
                    if not s3_url:
                        flash(f'No se pudo subir la imagen adicional {extra_file.filename} a S3.', 'danger')
                        continue
                    img_url = s3_url
                else:
                    filename = secure_filename(extra_file.filename)
                    upload_path = os.path.join(app.root_path, 'static', 'uploads', filename)
                    extra_file.save(upload_path)
                    img_url = url_for('static', filename=f'uploads/{filename}')
                db.session.add(ProductImage(product_id=product.id, image_url=img_url))
        db.session.commit()
        flash('Product added!', 'success')
        return redirect(url_for('admin.products'))
    return render_template('pages/admin/product_form.html', product=None)

@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if not session.get('is_admin'):
        abort(403)
    product = db.session.query(Product).get(product_id)
    if not product:
        abort(404)
    if request.method == 'POST':
        is_production = os.environ.get('FLASK_ENV') == 'production' or os.environ.get('RAILWAY_STATIC_URL') or os.environ.get('RAILWAY_ENVIRONMENT')
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = request.form['price']
        product.is_available = request.form.get('is_available', '1') == '1'
        image_url = request.form['image_url']
        file = request.files.get('image_file')
        if file and file.filename:
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[-1].lower()
            if ext not in app.config['ALLOWED_EXTENSIONS']:
                flash('Invalid image file type.', 'danger')
                return render_template('pages/admin/product_form.html', product=product)
            # is_production is now defined at the top of the POST block
            if is_production and app.config.get('S3_BUCKET'):
                s3_url = upload_file_to_s3(file, app.config['S3_BUCKET'])
                if not s3_url:
                    flash('Failed to upload image to S3.', 'danger')
                    return render_template('pages/admin/product_form.html', product=product)
                image_url = s3_url
            else:
                upload_path = os.path.join(app.root_path, 'static', 'uploads', filename)
                file.save(upload_path)
                image_url = url_for('static', filename=f'uploads/{filename}')
        product.image_url = image_url
        db.session.commit()
        # Handle multiple extra images
        extra_images = request.files.getlist('extra_images')
        for extra_file in extra_images:
            if extra_file and extra_file.filename:
                ext = extra_file.filename.rsplit('.', 1)[-1].lower()
                if ext not in app.config['ALLOWED_EXTENSIONS']:
                    flash(f'Archivo de imagen adicional inválido: {extra_file.filename}', 'danger')
                    continue
                if is_production and app.config.get('S3_BUCKET'):
                    s3_url = upload_file_to_s3(extra_file, app.config['S3_BUCKET'])
                    if not s3_url:
                        flash(f'No se pudo subir la imagen adicional {extra_file.filename} a S3.', 'danger')
                        continue
                    img_url = s3_url
                else:
                    filename = secure_filename(extra_file.filename)
                    upload_path = os.path.join(app.root_path, 'static', 'uploads', filename)
                    extra_file.save(upload_path)
                    img_url = url_for('static', filename=f'uploads/{filename}')
                db.session.add(ProductImage(product_id=product.id, image_url=img_url))
        db.session.commit()
        flash('Product updated!', 'success')
        return redirect(url_for('admin.products'))
    return render_template('pages/admin/product_form.html', product=product)

@admin_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    if not session.get('is_admin'):
        abort(403)
    product = db.session.query(Product).get(product_id)
    if not product:
        abort(404)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted!', 'success')
    return redirect(url_for('admin.products'))

@admin_bp.route('/products/delete-image/<int:image_id>/<int:product_id>', methods=['POST'])
@login_required
def delete_product_image(image_id, product_id):
    if not session.get('is_admin'):
        abort(403)
    img = db.session.query(ProductImage).get(image_id)
    if img:
        db.session.delete(img)
        db.session.commit()
        flash('Imagen eliminada.', 'success')
    else:
        flash('No se encontró la imagen.', 'danger')
    return redirect(url_for('admin.edit_product', product_id=product_id))

app.register_blueprint(admin_bp, url_prefix='/admin')

# Ensure upload directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CHAT_IMAGES_FOLDER'], exist_ok=True)

# Chatbot API route
# @app.route('/api/chat', methods=['POST'])
# def chat_api():
#     # Check if the request is form data or JSON
#     if request.is_json:
#         data = request.get_json()
#         question = data.get('question', '') or data.get('message', '')
#     else:
#         # Handle form data
#         question = request.form.get('message', '') or request.form.get('question', '')
#     
#     if not question:
#         return jsonify({'error': 'No question or message provided'}), 400
#     
#     try:
#         response = ask_wingfoil_ai(question)
#         return jsonify({'response': response})
#     except Exception as e:
#         app.logger.error(f"Error in chat_api: {str(e)}")
#         return jsonify({'error': str(e)}), 500

# Chatbot with image API route
# @app.route('/api/chat_with_image', methods=['POST'])
# def chat_with_image_api():
#     question = request.form.get('question', '')
#     image = request.files.get('image')
#     
#     if not image:
#         return jsonify({'error': 'No image provided'}), 400
#     
#     try:
#         # Save the image
#         filename = secure_filename(image.filename)
#         timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
#         unique_filename = f"{timestamp}_{filename}"
#         image_path = os.path.join(app.config['CHAT_IMAGES_FOLDER'], unique_filename)
#         
#         # Get response from AI with image
#         response = ask_wingfoil_ai(question, image_path)
#         
#         return jsonify({'response': response})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

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
    # Auto-create admin after migrations
    import os
    if os.environ.get("CREATE_ADMIN_ON_START") == "1":
        from werkzeug.security import generate_password_hash
        from models import User
        from app import db
        if not User.query.filter_by(username="admin").first():
            admin = User(
                username="admin",
                email="admin@tudominio.com",
                password=generate_password_hash("TuPasswordSeguro"),
                name="Administrador",
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Usuario admin creado automáticamente.")
        else:
            print("El usuario admin ya existe.")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
