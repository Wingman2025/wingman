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

# Create Flask app
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'simple-wingfoil-app-key')
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'wingfoil.db')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'profile_pictures')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

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

# Database helper functions
def get_db():
    """Get a database connection."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize the database."""
    db = get_db()
    
    # Create user table
    db.execute('''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        profile_picture TEXT,
        nationality TEXT,
        age INTEGER,
        sports_practiced TEXT,
        location TEXT,
        wingfoiling_since TEXT,
        wingfoil_level TEXT,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create session table
    db.execute('''
    CREATE TABLE IF NOT EXISTS session (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        sport_type TEXT NOT NULL,
        duration INTEGER NOT NULL,
        rating INTEGER,
        location TEXT,
        notes TEXT,
        skills TEXT,
        skill_ratings TEXT,
        achievements TEXT,
        challenges TEXT,
        conditions TEXT,
        weather TEXT,
        wind_speed TEXT,
        equipment TEXT,
        water_conditions TEXT,
        FOREIGN KEY (user_id) REFERENCES user (id)
    )
    ''')
    
    # Create skill table
    db.execute('''
    CREATE TABLE IF NOT EXISTS skill (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT
    )
    ''')
    
    # Create goal table
    db.execute('''
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        target_date TEXT,
        status TEXT NOT NULL DEFAULT 'In Progress',
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        skill_id INTEGER,
        completed BOOLEAN DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES user (id),
        FOREIGN KEY (skill_id) REFERENCES skill (id)
    )
    ''')
    
    # Commit the changes
    db.commit()
    
    # Check if skills already exist
    cursor = db.execute('SELECT COUNT(*) FROM skill')
    count = cursor.fetchone()[0]
    
    # Add skills if none exist
    if count == 0:
        skills = [
            {
                'name': 'Wing Handling & Depowering',
                'description': 'Mastering your wing\'s power - knowing how to generate lift and quickly depower by turning the wing out of the wind - is fundamental for control.',
                'practice': 'Start in calm, low-wind conditions on land or shallow water; work on smoothly adjusting the wing\'s angle and quickly depowering when needed.',
                'category': 'Basic'
            },
            {
                'name': 'Board Balance & Foiling Stance',
                'description': 'A solid, centered stance is key to maintaining stability on the board while foiling.',
                'practice': 'Use balance drills on land (or a foam board) to practice proper foot positioning and body tension before moving into deeper water.',
                'category': 'Basic'
            },
            {
                'name': 'Water Start & Upwind Foiling',
                'description': 'The water start is your transition from lying down to standing up, crucial for heading upwind.',
                'practice': 'In shallow water, set your wing correctly, engage your core, and practice the forward weight transfer to catch the foil\'s lift for a smooth upwind start.',
                'category': 'Basic'
            },
            {
                'name': 'Foil Lift Control & Edge Work',
                'description': 'Adjusting your board\'s edge and shifting your weight influences the foil\'s angle, affecting lift and performance.',
                'practice': 'In controlled conditions, experiment with small edge adjustments to feel how subtle shifts affect your foil\'s lift.',
                'category': 'Intermediate'
            },
            {
                'name': 'Tack Maneuvers',
                'description': 'Tacking is an upwind turn where you steer your board into the wind. It requires seamless coordination between your body, board, and wing.',
                'practice': 'Drill wide, smooth tacks in moderate wind, focusing on the timing of your body\'s pivot and wing repositioning to regain balance quickly.',
                'category': 'Intermediate'
            },
            {
                'name': 'Gybe Maneuvers',
                'description': 'Gybing is the downwind turn, where you transition your wing power across your body.',
                'practice': 'Begin with wide gybes in safe conditions, gradually tightening your turns as you learn to manage the wing\'s movement and maintain stability.',
                'category': 'Intermediate'
            },
            {
                'name': 'Wind Window Positioning',
                'description': 'Knowing your wind window - the optimal area downwind where your wing works most efficiently - is critical for effective sailing.',
                'practice': 'Constantly monitor and adjust your wing angle relative to the wind during your sessions, ensuring it stays within the ideal window.',
                'category': 'Intermediate'
            },
            {
                'name': 'Dynamic Weight Shifting & Body Tension',
                'description': 'Swift weight shifts and maintaining body tension directly impact your foil\'s response and maneuverability.',
                'practice': 'Incorporate drills that require rapid, subtle weight adjustments while riding to develop muscle memory for effective transitions.',
                'category': 'Advanced'
            },
            {
                'name': 'Speed Management & Deceleration',
                'description': 'Using your wing angle, board tilt, and edge pressure to modulate speed is vital for safe riding and quick stops.',
                'practice': 'Experiment with de-powering your wing and engaging your edge during various wind conditions to learn precise speed control.',
                'category': 'Advanced'
            },
            {
                'name': 'Jumping & Aerial Maneuvers',
                'description': 'Controlled jumps add a freestyle element to wingfoiling, utilizing foil lift for aerial tricks.',
                'practice': 'Start with small hops, focusing on the timing of your pop and safe landings; as you build confidence, progress to more advanced aerial techniques.',
                'category': 'Advanced'
            },
            {
                'name': 'Transitioning in Variable Conditions',
                'description': 'Quickly adapting to sudden wind shifts, gusts, or choppy water ensures continuous control and safety.',
                'practice': 'In mixed conditions, drill rapid transitions between planing and edging to simulate gusts, honing your ability to rebalance on the fly.',
                'category': 'Advanced'
            },
            {
                'name': 'Safety, Recovery & Self-Rescue Techniques',
                'description': 'Knowing how to fall safely, recover, and perform self-rescue is essential for every wingfoiler.',
                'practice': 'Regularly simulate controlled falls in shallow water, practice de-powering your wing during a fall, and rehearse self-rescue drills to build confidence.',
                'category': 'Basic'
            }
        ]
        
        for skill in skills:
            db.execute(
                'INSERT INTO skill (name, description, practice, category) VALUES (?, ?, ?, ?)',
                (skill['name'], skill['description'], skill['practice'], skill['category'])
            )
        
        db.commit()
        print(f"Added {len(skills)} skills to the database.")
    
    db.close()

def migrate_db():
    """Migrate the database to the latest schema."""
    # Connect directly to the database file
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    
    # Check if we need to add new columns to the user table
    cursor = conn.execute("PRAGMA table_info(user)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Add new columns if they don't exist
    if 'nationality' not in columns:
        conn.execute("ALTER TABLE user ADD COLUMN nationality TEXT")
    if 'age' not in columns:
        conn.execute("ALTER TABLE user ADD COLUMN age INTEGER")
    if 'sports_practiced' not in columns:
        conn.execute("ALTER TABLE user ADD COLUMN sports_practiced TEXT")
    if 'location' not in columns:
        conn.execute("ALTER TABLE user ADD COLUMN location TEXT")
    if 'wingfoiling_since' not in columns:
        conn.execute("ALTER TABLE user ADD COLUMN wingfoiling_since TEXT")
    if 'wingfoil_level' not in columns:
        conn.execute("ALTER TABLE user ADD COLUMN wingfoil_level TEXT")
    
    conn.commit()
    conn.close()
    print("Database migration completed successfully")

# Initialize the database
if not os.path.exists(app.config['DATABASE']):
    init_db()
else:
    # Run migration for existing database
    migrate_db()

# Create blueprints
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
profile_bp = Blueprint('profile', __name__, url_prefix='/profile')
training_bp = Blueprint('training', __name__, url_prefix='/training')
skills_bp = Blueprint('skills', __name__, url_prefix='/skills')
levels_bp = Blueprint('levels', __name__, url_prefix='/levels')

# Login required decorator
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('user_id') is None:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

# Auth routes
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name', '')
        
        db = get_db()
        error = None
        
        if not username:
            error = 'Username is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute('SELECT id FROM user WHERE username = ?', (username,)).fetchone() is not None:
            error = f"User {username} is already registered."
        elif db.execute('SELECT id FROM user WHERE email = ?', (email,)).fetchone() is not None:
            error = f"Email {email} is already registered."
            
        if error is None:
            db.execute(
                'INSERT INTO user (username, email, password, created_at, name) VALUES (?, ?, ?, ?, ?)',
                (username, email, generate_password_hash(password), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), name)
            )
            db.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        
        flash(error, 'danger')
    
    return render_template('pages/auth/register.html', title='Register')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        db = get_db()
        error = None
        user = db.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()
        
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
            
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['name'] = user['name']
            flash(f'Welcome back, {user["name"] or user["username"]}!', 'success')
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
    db = get_db()
    
    if request.method == 'POST':
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file.filename != '':
                if allowed_file(file.filename):
                    # Secure the filename and save the file
                    filename = secure_filename(f"{session['user_id']}_{file.filename}")
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    
                    # Remove old profile picture if it exists
                    user = db.execute('SELECT profile_picture FROM user WHERE id = ?', (session['user_id'],)).fetchone()
                    if user['profile_picture']:
                        old_filepath = os.path.join(app.config['UPLOAD_FOLDER'], user['profile_picture'])
                        if os.path.exists(old_filepath):
                            os.remove(old_filepath)
                    
                    # Save new file and update database
                    file.save(filepath)
                    db.execute('UPDATE user SET profile_picture = ? WHERE id = ?', (filename, session['user_id']))
                    db.commit()
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
            wingfoil_level = request.form.get('wingfoil_level', '')
            
            # Convert empty age to NULL
            age = int(age) if age and age.isdigit() else None
            
            # Update the user profile
            db.execute('''
                UPDATE user 
                SET nationality = ?, 
                    age = ?, 
                    sports_practiced = ?, 
                    location = ?, 
                    wingfoiling_since = ?, 
                    wingfoil_level = ? 
                WHERE id = ?
            ''', (nationality, age, sports_practiced, location, wingfoiling_since, wingfoil_level, session['user_id']))
            db.commit()
            flash('Profile updated successfully', 'success')
            
        return redirect(url_for('auth.profile'))
    
    user = db.execute('SELECT * FROM user WHERE id = ?', (session['user_id'],)).fetchone()
    session_count = db.execute('SELECT COUNT(*) as count FROM session WHERE user_id = ?', 
                           (session['user_id'],)).fetchone()['count']
    
    return render_template('pages/auth/profile.html', title='My Profile', 
                       user=user, session_count=session_count)

# Main routes
@main_bp.route('/')
def index():
    # Get weather data for Tarifa, Spain
    weather_data = {
        'current': {
            'temp': 22,
            'description': 'Partly Cloudy',
            'icon': 'bi-cloud-sun-fill'
        },
        'wind': {
            'speed': 15,
            'direction': 'NE',
            'icon': 'bi-wind'
        },
        'water': {
            'temp': 18,
            'wave_height': 0.8,
            'icon': 'bi-water'
        }
    }
    
    try:
        # OpenWeatherMap API key - you would need to replace this with a real key
        api_key = "YOUR_API_KEY"
        city = "Tarifa,es"
        
        # Get current weather
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        
        # Uncomment this when you have a valid API key
        # response = requests.get(weather_url)
        # if response.status_code == 200:
        #     data = response.json()
        #     weather_data['current']['temp'] = round(data['main']['temp'])
        #     weather_data['current']['description'] = data['weather'][0]['description'].capitalize()
        #     
        #     # Set appropriate icon based on weather condition
        #     condition = data['weather'][0]['main'].lower()
        #     if 'clear' in condition:
        #         weather_data['current']['icon'] = 'bi-sun-fill'
        #     elif 'cloud' in condition:
        #         weather_data['current']['icon'] = 'bi-cloud-fill'
        #     elif 'rain' in condition or 'drizzle' in condition:
        #         weather_data['current']['icon'] = 'bi-cloud-rain-fill'
        #     elif 'thunderstorm' in condition:
        #         weather_data['current']['icon'] = 'bi-cloud-lightning-fill'
        #     elif 'snow' in condition:
        #         weather_data['current']['icon'] = 'bi-snow'
        #     
        #     # Wind data
        #     weather_data['wind']['speed'] = round(data['wind']['speed'] * 3.6)  # Convert m/s to km/h
        #     
        #     # Get direction
        #     deg = data['wind']['deg']
        #     directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        #     index = round(deg / 45) % 8
        #     weather_data['wind']['direction'] = directions[index]
    except Exception as e:
        print(f"Error fetching weather data: {e}")
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    return render_template('pages/index.html', title='Home', current_time=current_time, weather=weather_data)

@main_bp.route('/about')
def about():
    return render_template('pages/about.html', title='About')

# Training routes
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
        db = get_db()
        
        try:
            # Get the current user ID from the Flask session
            user_id = session.get('user_id')
            
            # Insert session with all columns
            cursor = db.execute('''
                INSERT INTO session (
                    user_id, date, sport_type, duration, rating, 
                    location, notes, skills, skill_ratings, 
                    achievements, challenges, conditions,
                    weather, wind_speed, equipment, water_conditions
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, date, sport_type, duration, rating, 
                location, notes, json.dumps(skills), json.dumps(skill_ratings),
                achievements, challenges, conditions,
                weather, wind_speed, equipment, water_conditions
            ))
            
            db.commit()
            
            # Get the ID of the inserted session
            session_id = cursor.lastrowid
            
            if request.headers.get('Accept') == 'application/json':
                return jsonify({
                    'success': True, 
                    'message': 'Training session logged successfully!',
                    'session_id': session_id
                })
            
            flash('Training session logged successfully!', 'success')
            return redirect(url_for('training.session_detail', session_id=session_id))
            
        except sqlite3.Error as e:
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'success': False, 'error': str(e)})
            flash('Error saving session: ' + str(e), 'error')
            return redirect(url_for('training.log_session'))
    
    # GET request - show form
    db = get_db()
    skills = db.execute('SELECT * FROM skill ORDER BY category, name').fetchall()
    
    # Group skills by category
    skill_categories = {}
    for skill in skills:
        category = skill['category']
        if category not in skill_categories:
            skill_categories[category] = []
        skill_categories[category].append(skill)
    
    return render_template('pages/training/log_session.html', skill_categories=skill_categories)

@training_bp.route('/session/<int:session_id>')
@login_required
def session_detail(session_id):
    db = get_db()
    
    # Get session details
    cursor = db.execute('SELECT * FROM session WHERE id = ? AND user_id = ?', 
                       (session_id, session['user_id']))
    session_data = cursor.fetchone()
    
    if not session_data:
        flash('Session not found or you do not have permission to view it', 'danger')
        return redirect(url_for('training.stats'))
    
    # Get skills practiced in this session
    practiced_skill_ids = []
    skill_ratings = {}
    
    if session_data['skills']:
        try:
            practiced_skill_ids = json.loads(session_data['skills'])
            # Convert all IDs to strings for consistent comparison
            practiced_skill_ids = [str(skill_id) for skill_id in practiced_skill_ids]
        except:
            practiced_skill_ids = []
    
    if session_data['skill_ratings']:
        try:
            skill_ratings = json.loads(session_data['skill_ratings'])
        except:
            skill_ratings = {}
    
    # Initialize skills as an empty list
    skills = []
    
    if practiced_skill_ids and len(practiced_skill_ids) > 0:
        placeholders = ','.join(['?'] * len(practiced_skill_ids))
        cursor = db.execute(f'SELECT * FROM skill WHERE id IN ({placeholders})', practiced_skill_ids)
        skills_rows = cursor.fetchall()
        
        # Convert sqlite3.Row objects to dictionaries
        for skill_row in skills_rows:
            skill = dict(skill_row)
            skill_id = str(skill['id'])
            if skill_id in skill_ratings:
                skill['rating'] = skill_ratings[skill_id]
            skills.append(skill)
    
    # Get all skills for the edit form
    cursor = db.execute('SELECT * FROM skill ORDER BY category, name')
    all_skills = cursor.fetchall()
    
    # Group skills by category for the form
    skill_categories = {}
    for skill in all_skills:
        category = skill['category']
        if category not in skill_categories:
            skill_categories[category] = []
        skill_categories[category].append(dict(skill))
    
    # Convert session_data to a dictionary
    session_dict = dict(session_data)
    
    return render_template('pages/training/session_detail.html', 
                          title='Session Details', 
                          session=session_dict, 
                          skills=skills,
                          skill_categories=skill_categories,
                          practiced_skill_ids=practiced_skill_ids,
                          skill_ratings=skill_ratings)

@training_bp.route('/')
@login_required
def stats():
    db = get_db()
    cursor = db.execute('''
        SELECT * FROM session 
        WHERE user_id = ?
        ORDER BY date DESC
    ''', (session['user_id'],))
    sessions = cursor.fetchall()
    
    # Get top skills for the user
    cursor = db.execute('''
        SELECT s.name, AVG(CAST(json_extract(skill_ratings, '$."' || s.id || '"') AS REAL)) as avg_rating,
        COUNT(se.id) as session_count
        FROM skill s
        JOIN session se ON se.user_id = ? AND se.skills LIKE '%"' || s.id || '"%'
        GROUP BY s.id
        ORDER BY avg_rating DESC
        LIMIT 6
    ''', (session['user_id'],))
    skills_data = cursor.fetchall()
    
    # Format skills data for the template
    top_skills = []
    for skill in skills_data:
        rating = round(skill['avg_rating'], 1)
        level = 'beginner'
        if rating >= 3:
            level = 'intermediate'
        if rating >= 4:
            level = 'advanced'
            
        top_skills.append({
            'name': skill['name'],
            'rating': rating,
            'level': level,
            'session_count': skill['session_count']
        })
    
    # Get user goals
    try:
        cursor = db.execute('''
            SELECT g.*, s.name as skill_name, s.category as skill_category 
            FROM goals g
            LEFT JOIN skill s ON g.skill_id = s.id
            WHERE g.user_id = ? 
            ORDER BY g.completed, g.target_date
        ''', (session['user_id'],))
        goals = cursor.fetchall()
    except sqlite3.OperationalError:
        # If the goal table doesn't exist or has schema issues
        goals = []
    
    # Get all skills for the goal form
    cursor = db.execute('SELECT id, name, category FROM skill ORDER BY category, name')
    all_skills = cursor.fetchall()
    
    # Get user data including profile picture
    user = db.execute('SELECT * FROM user WHERE id = ?', (session['user_id'],)).fetchone()
    
    return render_template('pages/training/stats.html', 
                          title='Your Wingfoil Journey', 
                          user=user,
                          sessions=sessions,
                          top_skills=top_skills,
                          goals=goals,
                          all_skills=all_skills)

@training_bp.route('/api/sessions')
@login_required
def api_sessions():
    db = get_db()
    cursor = db.execute('''
        SELECT id, date, sport_type, duration, rating, location, notes, skills, skill_ratings,
               achievements, challenges, conditions, weather, wind_speed, equipment, water_conditions
        FROM session 
        WHERE user_id = ?
        ORDER BY date DESC
    ''', (session['user_id'],))
    sessions = cursor.fetchall()
    
    # Convert to list of dicts for JSON serialization
    sessions_data = []
    for s in sessions:
        # Create a dict with session data
        session_dict = {
            'id': s['id'],
            'date': s['date'],
            'sport_type': s['sport_type'],
            'duration': s['duration'],
            'rating': s['rating'],
            'location': s['location'],
            'notes': s['notes'],
            'achievements': s['achievements'],
            'challenges': s['challenges'],
            'conditions': s['conditions'],
            'weather': s['weather'],
            'wind_speed': s['wind_speed'],
            'equipment': s['equipment'],
            'water_conditions': s['water_conditions']
        }
        
        # Parse skills and skill_ratings JSON
        if s['skills']:
            try:
                session_dict['skills'] = json.loads(s['skills'])
            except:
                session_dict['skills'] = []
        else:
            session_dict['skills'] = []
            
        if s['skill_ratings']:
            try:
                session_dict['skill_ratings'] = json.loads(s['skill_ratings'])
            except:
                session_dict['skill_ratings'] = {}
        else:
            session_dict['skill_ratings'] = {}
            
        sessions_data.append(session_dict)
    
    return jsonify({'success': True, 'sessions': sessions_data})

@training_bp.route('/session/delete', methods=['POST'])
@login_required
def delete_session():
    db = get_db()
    session_id = request.form.get('session_id')
    
    if not session_id:
        return jsonify({'success': False, 'error': 'No session ID provided'})
    
    try:
        db.execute('DELETE FROM session WHERE id = ? AND user_id = ?', 
                  (session_id, session['user_id']))
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@training_bp.route('/session/update', methods=['POST'])
@login_required
def update_session():
    db = get_db()
    
    # Get form data
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
    
    # Get skills and skill ratings
    skills = request.form.getlist('skills')
    skill_ratings = request.form.get('skill_ratings', '{}')
    
    # Validate required fields
    if not all([session_id, date, sport_type, duration]):
        flash('Please fill in all required fields', 'danger')
        return redirect(url_for('training.session_detail', session_id=session_id))
    
    try:
        # Validate that session belongs to current user
        cursor = db.execute('SELECT user_id FROM session WHERE id = ?', (session_id,))
        session_data = cursor.fetchone()
        
        if not session_data or session_data['user_id'] != session['user_id']:
            flash('Session not found or you do not have permission to edit it', 'danger')
            return redirect(url_for('training.stats'))
        
        # Update session in database
        db.execute('''
            UPDATE session 
            SET date = ?, sport_type = ?, duration = ?, rating = ?,
                location = ?, notes = ?, skills = ?, skill_ratings = ?,
                achievements = ?, challenges = ?, conditions = ?,
                weather = ?, wind_speed = ?, equipment = ?, water_conditions = ?
            WHERE id = ? AND user_id = ?
        ''', (
            date, sport_type, duration, rating, location, notes, 
            json.dumps(skills), skill_ratings, achievements, challenges, 
            conditions, weather, wind_speed, equipment, water_conditions,
            session_id, session['user_id']
        ))
        
        db.commit()
        flash('Session updated successfully', 'success')
        return redirect(url_for('training.session_detail', session_id=session_id))
    
    except Exception as e:
        db.rollback()
        flash(f'Error updating session: {str(e)}', 'danger')
        return redirect(url_for('training.session_detail', session_id=session_id))

@training_bp.route('/goals/add', methods=['POST'])
@login_required
def add_goal():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description', '')
        target_date = request.form.get('target_date')
        skill_id = request.form.get('skill_id')
        
        # Validate required fields
        if not title:
            flash('Goal title is required', 'error')
            return redirect(url_for('training.stats'))
        
        db = get_db()
        
        try:
            # Add the current timestamp for created_at
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            db.execute('''
                INSERT INTO goals (user_id, title, description, target_date, skill_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (session['user_id'], title, description, target_date, skill_id, current_time))
            db.commit()
            flash('Goal added successfully!', 'success')
        except sqlite3.Error as e:
            db.rollback()
            flash('Error adding goal: ' + str(e), 'error')
        
        return redirect(url_for('training.stats'))

@training_bp.route('/goals/update-progress', methods=['POST'])
@login_required
def update_goal_progress():
    if request.method == 'POST':
        goal_id = request.form.get('goal_id')
        progress = request.form.get('progress')
        
        if not goal_id or not progress:
            return jsonify({'success': False, 'error': 'Missing required fields'})
        
        db = get_db()
        try:
            db.execute('''
                UPDATE goals 
                SET progress = ?, 
                    completed = CASE WHEN ? >= 100 THEN 1 ELSE 0 END
                WHERE id = ? AND user_id = ?
            ''', (progress, progress, goal_id, session['user_id']))
            db.commit()
            return jsonify({'success': True})
        except sqlite3.Error as e:
            return jsonify({'success': False, 'error': str(e)})

@training_bp.route('/goals/update', methods=['POST'])
@login_required
def update_goal():
    if request.method == 'POST':
        goal_id = request.form.get('goal_id')
        title = request.form.get('title')
        description = request.form.get('description', '')
        target_date = request.form.get('target_date')
        skill_id = request.form.get('skill_id')
        progress = request.form.get('progress', 0)
        
        # Validate required fields
        if not goal_id or not title:
            flash('Goal ID and title are required', 'error')
            return redirect(url_for('training.stats'))
        
        db = get_db()
        
        try:
            # Update the goal with all fields
            db.execute('''
                UPDATE goals 
                SET title = ?, 
                    description = ?, 
                    target_date = ?, 
                    skill_id = ?,
                    progress = ?,
                    completed = CASE WHEN ? >= 100 THEN 1 ELSE 0 END
                WHERE id = ? AND user_id = ?
            ''', (title, description, target_date, skill_id, progress, progress, goal_id, session['user_id']))
            db.commit()
            flash('Goal updated successfully!', 'success')
        except sqlite3.Error as e:
            db.rollback()
            flash('Error updating goal: ' + str(e), 'error')
        
        return redirect(url_for('training.stats'))

@training_bp.route('/goals/delete', methods=['POST'])
@login_required
def delete_goal():
    if request.method == 'POST':
        goal_id = request.form.get('goal_id')
        
        if not goal_id:
            return jsonify({'success': False, 'error': 'No goal ID provided'})
        
        db = get_db()
        try:
            db.execute('DELETE FROM goals WHERE id = ? AND user_id = ?', 
                      (goal_id, session['user_id']))
            db.commit()
            return jsonify({'success': True})
        except sqlite3.Error as e:
            return jsonify({'success': False, 'error': str(e)})

# Skills routes
@skills_bp.route('/')
@login_required
def skills_index():
    db = get_db()
    
    # Get all skills grouped by category
    cursor = db.execute('''
        SELECT s.*, 
               COUNT(DISTINCT ss.id) as session_count,
               AVG(CAST(json_extract(ss.skill_ratings, '$."' || s.id || '"') AS FLOAT)) as avg_rating
        FROM skill s
        LEFT JOIN session ss ON json_extract(ss.skills, '$') LIKE '%' || s.id || '%'
            AND ss.user_id = ?
        GROUP BY s.id
        ORDER BY s.category, s.name
    ''', (session['user_id'],))
    
    skills = {}
    for skill in cursor:
        category = skill['category']
        if category not in skills:
            skills[category] = []
        
        # Calculate the skill level based on average rating
        avg_rating = skill['avg_rating'] or 0
        level = 'beginner'
        if avg_rating >= 3:
            level = 'intermediate'
        if avg_rating >= 4:
            level = 'advanced'
        
        skill_dict = dict(skill)
        skill_dict['level'] = level
        skill_dict['avg_rating'] = round(avg_rating, 1) if avg_rating else 0
        skills[category].append(skill_dict)
    
    return render_template('pages/skills/index.html', 
                         title='Skills Overview',
                         skills=skills)

@skills_bp.route('/skill/<int:skill_id>')
@login_required
def skill_detail(skill_id):
    db = get_db()
    
    # Get skill details
    cursor = db.execute('SELECT * FROM skill WHERE id = ?', (skill_id,))
    skill = cursor.fetchone()
    
    if not skill:
        flash('Skill not found', 'error')
        return redirect(url_for('skills.skills_index'))
    
    # Get sessions where this skill was practiced
    cursor = db.execute('''
        SELECT s.*, 
               json_extract(s.skill_ratings, '$.' || ?) as skill_rating
        FROM session s
        WHERE s.user_id = ?
            AND json_extract(s.skills, '$') LIKE '%' || ? || '%'
        ORDER BY s.date DESC
    ''', (skill_id, session['user_id'], skill_id))
    sessions = cursor.fetchall()
    
    # Calculate statistics
    total_sessions = len(sessions)
    avg_rating = 0
    if total_sessions > 0:
        ratings = [float(s['skill_rating'] or 0) for s in sessions]
        avg_rating = round(sum(ratings) / len(ratings), 1)
    
    # Get user's goals for this skill
    cursor = db.execute('''
        SELECT * FROM goals 
        WHERE user_id = ? AND skill_id = ?
        ORDER BY completed, target_date
    ''', (session['user_id'], skill_id))
    goals = cursor.fetchall()
    
    return render_template('pages/skills/detail.html',
                         title=skill['name'],
                         skill=skill,
                         sessions=sessions,
                         total_sessions=total_sessions,
                         avg_rating=avg_rating,
                         goals=goals)

@skills_bp.route('/api/skill/<int:skill_id>')
@login_required
def get_skill_details(skill_id):
    db = get_db()
    
    # Get skill details
    cursor = db.execute('SELECT * FROM skill WHERE id = ?', (skill_id,))
    skill = cursor.fetchone()
    
    if not skill:
        return jsonify({'success': False, 'error': 'Skill not found'})
    
    # Get sessions where this skill was practiced
    cursor = db.execute('''
        SELECT s.*, 
               json_extract(s.skill_ratings, '$.' || ?) as skill_rating
        FROM session s
        WHERE s.user_id = ?
            AND json_extract(s.skills, '$') LIKE '%' || ? || '%'
        ORDER BY s.date DESC
        LIMIT 5
    ''', (skill_id, session['user_id'], skill_id))
    recent_sessions = cursor.fetchall()
    
    # Format sessions for JSON response
    sessions_data = []
    for s in recent_sessions:
        session_dict = {
            'id': s['id'],
            'date': s['date'],
            'rating': float(s['skill_rating'] or 0),
            'notes': s['notes']
        }
        sessions_data.append(session_dict)
    
    # Calculate statistics
    cursor = db.execute('''
        SELECT COUNT(*) as total_sessions,
               AVG(CAST(json_extract(skill_ratings, '$.' || ?) AS FLOAT)) as avg_rating
        FROM session
        WHERE user_id = ?
            AND json_extract(skills, '$') LIKE '%' || ? || '%'
    ''', (skill_id, session['user_id'], skill_id))
    stats = cursor.fetchone()
    
    response_data = {
        'success': True,
        'skill': dict(skill),
        'recent_sessions': sessions_data,
        'stats': {
            'total_sessions': stats['total_sessions'],
            'avg_rating': round(stats['avg_rating'] or 0, 1)
        }
    }
    
    return jsonify(response_data)

# Levels routes
@levels_bp.route('/')
@login_required
def levels_index():
    return render_template('pages/levels/index.html')

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(main_bp)
app.register_blueprint(training_bp, url_prefix='/training')
app.register_blueprint(skills_bp, url_prefix='/skills')
app.register_blueprint(levels_bp, url_prefix='/levels')

@app.teardown_appcontext
def close_db_connection(exception):
    close_db(exception)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5010)
