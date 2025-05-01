import sys
import os

# Add the project directory to the Python path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

# Import the Flask app
from app import app as application

# The initialize_database() call was removed from here
# as migrations are run via the Procfile before gunicorn starts.

# PythonAnywhere looks for an 'application' object by default
if __name__ == '__main__':
    application.run(debug=False)
