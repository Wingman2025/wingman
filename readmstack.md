# Wingman Project Technology Stack

The Wingman project leverages a robust and modern technology stack to deliver a scalable, secure, and intelligent web application experience. Below is a summary of the core technologies and services used:

## Backend
- **Python**: Primary programming language for backend logic.
- **Flask**: Lightweight web framework used to build the API and serve web pages.
- **WSGI (Web Server Gateway Interface)**: Used for running the Flask app in production environments.
- **PostgreSQL**: Relational database for storing user data, skills, sessions, and application state. Used both in local development and production (Railway).

## Frontend
- **HTML5, CSS3, JavaScript**: Standard web technologies for building responsive user interfaces.
- **Jinja2**: Templating engine integrated with Flask for dynamic HTML rendering.

## AI & Chatbot
- **OpenAI GPT-4o (Responses API)**: Provides advanced conversational AI capabilities. The chatbot uses the `client.responses.create` method to interact with users and returns structured JSON responses (including message, tips, and equipment recommendations).

## Deployment & Infrastructure
- **Railway**: Cloud platform used for deploying the application in production. Handles PostgreSQL database hosting and web server deployment.

## Additional Libraries & Tools
- **psycopg2**: PostgreSQL database adapter for Python.
- **Flask-Login**: Manages user authentication and session management.
- **gunicorn**: WSGI HTTP server for running the Flask application in production.

## Security & Best Practices
- User authentication and session management are handled securely with Flask-Login.
- Sensitive credentials and API keys are managed via environment variables.

---

## Process Flow & File Interactions

Below is an explanation of how the main Python files in the Wingman project interact to deliver the application's functionality:

### 1. `run.py` — Application Entrypoint
- **Purpose:** This file serves as the entrypoint for running the application, especially in production environments like Railway.
- **Flow:**
  - Imports the Flask `app` object, database instance (`db`), and the `initialize_database` function from `app.py`.
  - Detects the environment (local or Railway cloud) and initializes the database accordingly.
  - Starts the Flask application by calling `app.run()` with appropriate host and port settings.

### 2. `app.py` — Main Application Logic
- **Purpose:** Central file for the Flask application, route definitions, and integration of all modules.
- **Key Responsibilities:**
  - Configures the Flask app, environment variables, and database connection.
  - Initializes SQLAlchemy (`db`), Flask-Migrate, and sets up Jinja2 filters.
  - Imports models from `models.py` and chatbot logic from `chatbot.py`.
  - Registers blueprints for modular route management (auth, main, training, skills, levels, profile, admin, etc.).
  - Defines routes for user registration, login, profile, training dashboards, session logging, and admin interfaces.
  - Provides API endpoints for chatbot interactions (routes like `/chat_api` and `/chat_with_image_api` call functions from `chatbot.py`).
  - Utility functions for file uploads, allowed file checks, and database migrations.

### 3. `models.py` — Database Models
- **Purpose:** Contains all SQLAlchemy ORM model definitions for the application's data structures.
- **Key Models:**
  - `User`, `Session`, `SessionImage`, `Skill`, `Goal`, `Level`, and `LearningMaterial`.
  - Defines relationships between users, sessions, skills, goals, and learning materials.
  - The `db` instance is created here and initialized with the Flask app in `app.py`.
- **Flow:**
  - Models are imported into `app.py` for database operations (user management, session logging, skills, etc.).

### 4. `chatbot.py` — AI/Chatbot Logic
- **Purpose:** Implements the logic to interact with the OpenAI GPT-4o Responses API for chatbot functionality.
- **Key Functions:**
  - `ask_wingfoil_ai(question, image_path=None)`: Handles the preparation of input (text and optional image), calls the OpenAI API, and returns structured JSON responses.
  - Flask routes for chatbot endpoints (if run independently).
- **Flow:**
  - The `ask_wingfoil_ai` function is imported and used in `app.py` for chatbot-related API routes.
  - When a user interacts with the chatbot (e.g., via `/chat_api`), the request is processed in `app.py`, which calls the function in `chatbot.py` and returns the AI's response to the frontend.

---

### **Summary of Interaction**
- **`run.py`** starts the app and ensures the DB is ready.
- **`app.py`** is the core, wiring together routes, database, and chatbot logic.
- **`models.py`** provides the data structure and ORM for all persistent data.
- **`chatbot.py`** handles all AI-related queries and is invoked by routes in `app.py`.

