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

### Quick Reference: Database Migration Workflow

1. **Create/Update Models:**
   - Add or change models in `models.py`.
2. **Generate Migration:**
   - Run: `flask db revision --autogenerate -m "Describe your change"`
   - A new migration file appears in `migrations/versions/`.
3. **Apply Migration Locally:**
   - Run: `flask db upgrade`
   - Confirm changes in your local database.
4. **Commit & Push:**
   - Commit migration files and code changes to your feature branch.
   - Merge your branch into the production branch (e.g., `main`).
5. **Deploy & Upgrade in Production:**
   - Deploy the production branch to Railway.
   - Ensure `flask db upgrade` runs (via `Procfile` release command or manually).
   - Alembic applies any new migrations to the production DB.
6. **Verify:**
   - Check the Railway Data tab to confirm new tables/columns exist.

**Note:** Migrations are only applied in production after merging and deploying the branch containing the migration files.


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
  - The user profile route (`/profile/`) is now handled by its own blueprint (`profile_bp`), separated from authentication routes. This improves code organization and makes it easier to extend profile-related functionality. The endpoint for the profile page is now `profile.profile` (was previously `auth.profile`).
  - The authentication blueprint (`auth_bp`) is registered with the prefix `/auth`. All authentication-related links in templates (login, logout, register) should use `url_for('auth.X')` endpoints (e.g., `url_for('auth.logout')`). This avoids routing errors and makes the app structure more maintainable.
  - Defines routes for user registration, login, profile, training dashboards, session logging, and admin interfaces.
  - Provides API endpoints for chatbot interactions (routes like `/chat_api` and `/chat_with_image_api` call functions from `chatbot.py`).

### 3. `models.py` — Database Models Overview
- **Purpose:** Defines the core data models and their relationships using SQLAlchemy ORM.
- **Key Models:**
  - **User:** Stores user credentials, profile info, admin flag, and is related to sessions and goals.
    - Fields: `id`, `username`, `password`, `email`, `name`, `profile_picture`, `is_admin`, `nationality`, `age`, `sports_practiced`, `location`, `wingfoiling_since`, `wingfoil_level`, `wingfoil_level_id`, `created_at`
    - Relationships: Has many `Session` and `Goal` objects; links to a `Level`.
  - **Session:** Represents a training session for a user.
    - Fields: `id`, `user_id`, `date`, `sport_type`, `duration`, `rating`, `location`, `notes`, `skills`, `skill_ratings`, `achievements`, `challenges`, `conditions`, `weather`, `wind_speed`, `equipment`, `water_conditions`, `instructor_feedback`, `student_feedback`
    - Relationships: Belongs to a `User`; has many `SessionImage` and `LearningMaterial` objects.
  - **SessionImage:** Stores image URLs related to a session.
    - Fields: `id`, `session_id`, `url`
    - Relationships: Belongs to a `Session`.
  - **Skill:** Catalog of skills, each with a category and description.
    - Fields: `id`, `name`, `category`, `description`, `created_at`
  - **Goal:** User-defined goals for progression.
    - Fields: `id`, `user_id`, `title`, `description`, `due_date`, `created_at`
    - Relationships: Belongs to a `User`.
  - **Level:** Represents wingfoil progression levels.
    - Fields: `id`, `code`, `name`, `description`, `created_at`
    - Relationships: Linked to users via `wingfoil_level_id`.
  - **LearningMaterial:** Stores educational resources (e.g., YouTube links) for sessions.
    - Fields: `id`, `session_id`, `url`, `title`, `thumbnail_url`, `created_at`
    - Relationships: Belongs to a `Session`.
  - **Product:** Represents gear/equipment for the Gear page.
    - Fields: `id`, `name`, `description`, `price`, `image_url`, `is_available`, `created_at`

- **Relationships:**
  - Users can have multiple sessions and goals.
  - Sessions can have multiple images and learning materials.
  - Levels classify users and progression.
  - Products are standalone and used for the Gear page.
  - Utility functions for file uploads, allowed file checks, and database migrations.


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

---

### Admin Functionality & Management

**Purpose:** The admin interface provides privileged users (admins) with tools to manage users, training sessions, and gear/products.

#### **Admin Rights & Access**
- Only users with `is_admin=True` in the database can access admin pages.
- Admin routes are protected: non-admins are redirected or shown an access denied message.
- Admin login is available at `/admin/login`.

#### **Admin Features**
- **Dashboard:** `/admin/dashboard` — Overview of all users, session counts, and feedback statistics.
- **Session Management:** `/admin/sessions` — View, edit, and manage all training sessions for all users.
- **Product (Gear) Management:** `/admin/products` — Add, edit, or delete gear/products shown on the public Gear page. Includes product forms and image URL support.
- **User Management:** View user profiles and stats (via dashboard; can be extended for more control).

#### **Admin Workflow**
1. **Login:** Visit `/admin/login` and authenticate with admin credentials.
2. **Navigate:** Use dashboard links or go directly to `/admin/products` to manage gear, or `/admin/sessions` for session management.
3. **Manage:** Add, update, or delete products; view and edit session details; review user feedback and stats.

#### **Security Notes**
- Only admins can access or modify data through admin routes.
- Admin status is set via the `is_admin` field on the User model (see `create_admin.py` for setup).
- All sensitive actions (like deleting products) require confirmation and are logged via flash messages.

---