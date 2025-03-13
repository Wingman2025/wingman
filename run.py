import os
from app import app, initialize_database

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use the port assigned by Railway
    
    # Initialize the database within the application context
    with app.app_context():
        initialize_database()
    
    app.run(debug=False, host='0.0.0.0', port=port)
