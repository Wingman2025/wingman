# Simple WingFoil Progress Tracker

A simplified version of the WingFoil Progress Tracker application with a clean structure and minimal dependencies.

## Features

- **Training Session Logging**: Record your wingfoil sessions with date, duration, location, and rating
- **Skill Tracking**: Track specific skills practiced during each session
- **Progress Visualization**: View your training history and progress over time
- **User Authentication**: Register and login to track your personal training sessions
- **User Profiles**: View your account information and training statistics
- Browse skills organized by difficulty level (Basic, Intermediate, Advanced)
- View detailed information about each skill including practice techniques

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python run.py
   ```

3. Access the application in your browser at:
   ```
   http://127.0.0.1:5009
   ```

## Structure

- `app.py` - Main application file containing all routes and database logic
- `run.py` - Script to run the application
- `templates/` - HTML templates
- `static/` - Static assets (CSS, JavaScript)
- `wingfoil.db` - SQLite database (created automatically on first run)

## Dependencies

- Flask 2.0.1
- Werkzeug 2.0.1
- Jinja2 3.0.1
- Other dependencies listed in requirements.txt

## Deployment to PythonAnywhere

Follow these steps to deploy the application to PythonAnywhere:

1. **Create a PythonAnywhere account**
   - Sign up for a free account at [PythonAnywhere](https://www.pythonanywhere.com/)

2. **Upload your code**
   - From the Dashboard, go to the "Files" tab
   - Create a new directory (e.g., `wingfoil`)
   - Upload all your project files to this directory
   - Alternatively, use Git to clone your repository:
     ```
     git clone https://github.com/yourusername/simple-wingfoil-app.git wingfoil
     ```

3. **Set up a virtual environment**
   - Open a Bash console from the Dashboard
   - Navigate to your project directory:
     ```
     cd wingfoil
     ```
   - Create a virtual environment:
     ```
     mkvirtualenv --python=/usr/bin/python3.9 wingfoil-venv
     ```
   - Install dependencies:
     ```
     pip install -r requirements.txt
     ```

4. **Configure the Web app**
   - Go to the "Web" tab on the Dashboard
   - Click "Add a new web app"
   - Select "Manual configuration" and choose Python 3.9
   - Set the path to your project directory (e.g., `/home/yourusername/wingfoil`)
   - In the "Code" section, set the WSGI configuration file path to `/home/yourusername/wingfoil/wsgi.py`
   - Click on the WSGI configuration file link to edit it
   - Replace the contents with the code from your `wsgi.py` file
   - In the "Virtualenv" section, enter the path to your virtual environment (e.g., `/home/yourusername/.virtualenvs/wingfoil-venv`)

5. **Initialize the database**
   - Go back to the Bash console
   - Run Python and execute the following:
     ```python
     from app import app, init_db
     with app.app_context():
         init_db()
     ```

6. **Reload the web app**
   - Go back to the "Web" tab
   - Click the "Reload" button for your web app

Your WingFoil Progress Tracker should now be accessible at `yourusername.pythonanywhere.com`.

## Troubleshooting

- **Template not found errors**: Make sure all templates are in the correct directory structure
- **Database errors**: Check file permissions for the database file
- **Static files not loading**: Ensure the static files URL is configured correctly in PythonAnywhere
