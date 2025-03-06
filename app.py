import os
import sqlite3
import json
import re
from datetime import datetime
import requests
import functools
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, g, render_template, request, redirect, url_for, flash, session, jsonify, Blueprint

# Create Flask app
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'simple-wingfoil-app-key')
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'wingfoil.db')

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
    """Get a database connection"""
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def close_db(e=None):
    """Close the database connection at the end of the request"""
    if hasattr(app, 'db'):
        app.db.close()

def init_db():
    """Initialize the database with tables and sample data"""
    db = get_db()
    
    # Create tables
    db.execute('''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TEXT NOT NULL,
        name TEXT
    )
    ''')
    
    db.execute('''
    CREATE TABLE IF NOT EXISTS skill (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        practice TEXT,
        category TEXT
    )
    ''')
    
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
        FOREIGN KEY (user_id) REFERENCES user (id)
    )
    ''')
    
    db.execute('''
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        target_date TEXT NOT NULL,
        created_at TEXT NOT NULL,
        progress INTEGER DEFAULT 0,
        completed INTEGER DEFAULT 0,
        completed_at TEXT,
        FOREIGN KEY (user_id) REFERENCES user (id)
    )
    ''')
    
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

# Initialize the database
if not os.path.exists(app.config['DATABASE']):
    init_db()
    print("Database initialized successfully.")

# Create blueprints
main_bp = Blueprint('main', __name__)
training_bp = Blueprint('training', __name__)
skills_bp = Blueprint('skills', __name__)
auth_bp = Blueprint('auth', __name__)

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

@auth_bp.route('/profile')
@login_required
def profile():
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE id = ?', (session['user_id'],)).fetchone()
    
    # Get session count
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
        date = request.form.get('date')
        sport_type = request.form.get('sport_type')
        duration = request.form.get('duration')
        rating = request.form.get('rating')
        location = request.form.get('location')
        notes = request.form.get('notes')
        
        # Get selected skills and ratings
        skills = request.form.getlist('skills[]')
        skill_ratings = {}
        
        for skill_id in skills:
            rating_key = f'skill_rating_{skill_id}'
            if rating_key in request.form:
                skill_ratings[skill_id] = request.form.get(rating_key)
        
        # Save to database
        db = get_db()
        cursor = db.execute('''
            INSERT INTO session (user_id, date, sport_type, duration, rating, location, notes, skills, skill_ratings)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session['user_id'], 
            date, 
            sport_type, 
            duration, 
            rating, 
            location, 
            notes, 
            json.dumps(skills), 
            json.dumps(skill_ratings)
        ))
        db.commit()
        
        flash('Training session logged successfully!', 'success')
        return redirect(url_for('training.stats'))
    
    # Get all skills for the form
    db = get_db()
    cursor = db.execute('SELECT * FROM skill ORDER BY category, name')
    skills = cursor.fetchall()
    
    return render_template('pages/training/log_session.html', title='Log Training Session', skills=skills)

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
    cursor = db.execute('''
        SELECT * FROM goals 
        WHERE user_id = ? 
        ORDER BY completed, target_date
    ''', (session['user_id'],))
    goals = cursor.fetchall()
    
    return render_template('pages/training/stats.html', 
                          title='Your Wingfoil Journey', 
                          sessions=sessions,
                          top_skills=top_skills,
                          goals=goals)

@training_bp.route('/api/sessions')
@login_required
def api_sessions():
    db = get_db()
    cursor = db.execute('''
        SELECT id, date, sport_type, duration, rating, location, notes, skills, skill_ratings
        FROM session 
        WHERE user_id = ?
        ORDER BY date ASC
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
            'notes': s['notes']
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
    practiced_skill_ids = json.loads(session_data['skills'])
    skill_ratings = json.loads(session_data['skill_ratings'])
    
    # Get full skill details
    skills = []
    if practiced_skill_ids:
        placeholders = ','.join(['?'] * len(practiced_skill_ids))
        cursor = db.execute(f'SELECT * FROM skill WHERE id IN ({placeholders})', practiced_skill_ids)
        skills = cursor.fetchall()
        
        # Add ratings to skills
        for skill in skills:
            skill_id = str(skill['id'])
            if skill_id in skill_ratings:
                skill['rating'] = skill_ratings[skill_id]
    
    return render_template('pages/training/session_detail.html', 
                          title='Session Details', 
                          session=session_data, 
                          skills=skills)

@training_bp.route('/session/delete/<int:session_id>', methods=['POST'])
@login_required
def delete_session(session_id):
    db = get_db()
    
    # Verify ownership
    cursor = db.execute('SELECT user_id FROM session WHERE id = ?', (session_id,))
    session_data = cursor.fetchone()
    
    if not session_data or session_data['user_id'] != session['user_id']:
        return jsonify({'success': False, 'error': 'Permission denied'}), 403
    
    db.execute('DELETE FROM session WHERE id = ?', (session_id,))
    db.commit()
    
    return jsonify({'success': True})

@training_bp.route('/goals/add', methods=['POST'])
@login_required
def add_goal():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description', '')
        target_date = request.form.get('target_date')
        
        if not title or not target_date:
            flash('Title and target date are required', 'danger')
            return redirect(url_for('training.stats'))
        
        db = get_db()
        db.execute(
            'INSERT INTO goals (user_id, title, description, target_date, created_at) VALUES (?, ?, ?, ?, ?)',
            (session['user_id'], title, description, target_date, datetime.now().strftime('%Y-%m-%d'))
        )
        db.commit()
        
        flash('Goal added successfully!', 'success')
        return redirect(url_for('training.stats'))

@training_bp.route('/goals/update/<int:goal_id>', methods=['POST'])
@login_required
def update_goal(goal_id):
    progress = request.form.get('progress', 0, type=int)
    completed = 1 if progress == 100 else 0
    completed_at = datetime.now().strftime('%Y-%m-%d') if completed else None
    
    db = get_db()
    db.execute(
        'UPDATE goals SET progress = ?, completed = ?, completed_at = ? WHERE id = ? AND user_id = ?',
        (progress, completed, completed_at, goal_id, session['user_id'])
    )
    db.commit()
    
    return jsonify({'success': True})

@training_bp.route('/goals/delete/<int:goal_id>', methods=['POST'])
@login_required
def delete_goal(goal_id):
    db = get_db()
    db.execute('DELETE FROM goals WHERE id = ? AND user_id = ?', (goal_id, session['user_id']))
    db.commit()
    
    return jsonify({'success': True})

# Skills routes
@skills_bp.route('/')
def skills_index():
    db = get_db()
    cursor = db.execute('''
        SELECT * FROM skill 
        ORDER BY 
            CASE category 
                WHEN 'Basic' THEN 1 
                WHEN 'Intermediate' THEN 2 
                WHEN 'Advanced' THEN 3 
                ELSE 4 
            END, 
            name
    ''')
    all_skills = cursor.fetchall()
    
    # Organize skills by category
    basic_skills = []
    intermediate_skills = []
    advanced_skills = []
    
    for skill in all_skills:
        if skill['category'] == 'Basic':
            basic_skills.append(skill)
        elif skill['category'] == 'Intermediate':
            intermediate_skills.append(skill)
        else:
            advanced_skills.append(skill)
    
    return render_template('pages/skills/index.html', 
                          title='Skills', 
                          basic_skills=basic_skills,
                          intermediate_skills=intermediate_skills,
                          advanced_skills=advanced_skills)

@skills_bp.route('/skill/<int:skill_id>')
def skill_detail(skill_id):
    db = get_db()
    
    # Get skill details
    cursor = db.execute('SELECT * FROM skill WHERE id = ?', (skill_id,))
    skill = cursor.fetchone()
    
    if not skill:
        flash('Skill not found', 'danger')
        return redirect(url_for('skills.skills_index'))
    
    # Add additional information for the skill details page
    skill_info = dict(skill)
    
    # Add difficulty level description
    if skill_info['category'] == 'Basic':
        skill_info['difficulty_description'] = "Basic skills that form the foundation of wingfoiling. Suitable for beginners with little to no experience."
    elif skill_info['category'] == 'Intermediate':
        skill_info['difficulty_description'] = "Intermediate techniques that build upon basic skills. Suitable for riders who are comfortable with the fundamentals."
    else:
        skill_info['difficulty_description'] = "Advanced maneuvers that require significant experience and practice. For experienced riders looking to push their limits."
    
    # Add equipment recommendations
    if skill_info['category'] == 'Basic':
        skill_info['equipment'] = "Larger, more stable board (80-120L). Smaller wing (4-5m²) for lighter winds."
    elif skill_info['category'] == 'Intermediate':
        skill_info['equipment'] = "Medium-sized board (70-100L). Medium wing size (4-6m²) suitable for various conditions."
    else:
        skill_info['equipment'] = "Smaller, more maneuverable board (60-80L). Various wing sizes depending on the specific maneuver and conditions."
    
    # Add learning time estimation
    if skill_info['category'] == 'Basic':
        skill_info['learning_time'] = "2-5 sessions of focused practice for Basic skills"
    elif skill_info['category'] == 'Intermediate':
        skill_info['learning_time'] = "5-10 sessions of dedicated practice for Intermediate skills"
    else:
        skill_info['learning_time'] = "10+ sessions of intensive practice for Advanced skills"
    
    # Get related skills (same category)
    cursor = db.execute('''
        SELECT * FROM skill 
        WHERE category = ? AND id != ? 
        ORDER BY name
        LIMIT 3
    ''', (skill['category'], skill_id))
    related_skills = cursor.fetchall()
    
    # Add progression path
    if skill_info['category'] == 'Basic':
        next_level = 'Intermediate'
    elif skill_info['category'] == 'Intermediate':
        next_level = 'Advanced'
    else:
        next_level = None
        
    if next_level:
        cursor = db.execute('''
            SELECT * FROM skill 
            WHERE category = ? 
            ORDER BY RANDOM()
            LIMIT 2
        ''', (next_level,))
        skill_info['progression_skills'] = cursor.fetchall()
    else:
        skill_info['progression_skills'] = []
    
    return render_template('pages/skills/detail.html', 
                          title=skill['name'], 
                          skill=skill_info, 
                          related_skills=related_skills)

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(training_bp, url_prefix='/training')
app.register_blueprint(skills_bp, url_prefix='/skills')
app.register_blueprint(auth_bp, url_prefix='/auth')

# Close database connection at the end of each request
@app.teardown_appcontext
def close_db_connection(exception):
    close_db(exception)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5010)
