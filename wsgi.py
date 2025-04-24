import sys
import os

# Add the project directory to the Python path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

# Import the Flask app and initialization function
from app import app as application, initialize_database

with application.app_context():
    print("Initializing database migrations...")
    initialize_database()

# PythonAnywhere looks for an 'application' object by default
if __name__ == '__main__':
    application.run(debug=False)
