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
- **OpenAI Agents SDK (openai-agents-python)**: Manages the interaction with OpenAI's language models for the chatbot functionality.
- **OpenAI GPT-4o Model**: The specific language model used by the agent to provide expert wingfoil instruction.
- **Functionality**: The agent is configured in `agent.py` and exposed via a Flask blueprint at `/agent/api/chat`. It receives user messages and returns plain text replies.

### Testing the Agent Locally with cURL
To test the chatbot agent locally after starting the Flask server (`python run.py`):

1.  **Ensure your `OPENAI_API_KEY` environment variable is set.**

2.  **Create a JSON file for the request body**, for example, `agent_test_body.json` in the project root, with the following content:
    ```json
    {
      "message": "What are the common mistakes beginners make in wingfoil?"
    }
    ```

3.  **Open your terminal (Git Bash, PowerShell, or CMD on Windows) and run the following `curl` command** from the project's root directory:
    ```bash
    curl.exe -X POST http://127.0.0.1:5000/agent/api/chat -H "Content-Type: application/json" --data-binary "@agent_test_body.json"
    ```
    *(Note: Use `curl` instead of `curl.exe` if you are on macOS/Linux or using a shell that aliases it).*

4.  **Expected Output**: You should receive a JSON response from the agent, like:
    ```json
    {
      "reply": "One common mistake is not keeping the wing high enough..."
    }
    ```
    If you encounter errors, check the Flask server console output for details.

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
  - Imports models from `models.py` and the new chatbot agent blueprint from `agent.py`.
  - Registers blueprints for modular route management (auth, main, training, skills, levels, profile, admin, etc.).
  - The user profile route (`/profile/`) is now handled by its own blueprint (`profile_bp`), separated from authentication routes. This improves code organization and makes it easier to extend profile-related functionality. The endpoint for the profile page is now `profile.profile` (was previously `auth.profile`).
  - The authentication blueprint (`auth_bp`) is registered with the prefix `/auth`. All authentication-related links in templates (login, logout, register) should use `url_for('auth.X')` endpoints (e.g., `url_for('auth.logout')`). This avoids routing errors and makes the app structure more maintainable.
  - Defines routes for user registration, login, profile, training dashboards, session logging, and admin interfaces.
  - The new chatbot is available via the `/agent/api/chat` endpoint, managed by the blueprint in `agent.py`. Old chatbot routes (`/api/chat`, `/api/chat_with_image`) have been commented out.

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


### 4. `agent.py` — New AI/Chatbot Logic
- **Purpose:** Implements the chatbot logic using the `openai-agents-python` SDK.
- **Key Components:**
  - Defines a Flask Blueprint (`agent_bp`) mounted at `/agent`.
  - Initializes an OpenAI `Agent` configured with system instructions (to act as a wingfoil expert) and the `gpt-4o` model.
  - Provides an API endpoint `/api/chat` (full path `/agent/api/chat`) that accepts a user's message and uses an `AgentRunner` to get a reply.
- **Flow:**
  - The `agent_bp` blueprint is registered in `app.py`.
  - Frontend JavaScript calls the `/agent/api/chat` endpoint.
  - The `agent.py` module handles the interaction with the OpenAI API via the Agent SDK and returns a plain text response.

### Guardrail LLM (Filtro de Lenguaje)
- Implementado en `agent.py` como agente OpenAI para bloquear únicamente lenguaje inapropiado.
- Utiliza `GuardrailOutput` (Pydantic) con campos `is_inappropriate` y `reasoning`.
- `guardrail_agent` definido con instrucciones claras y modelo `gpt-4o`.
- Función decorada `@input_guardrail inappropriate_guardrail` intercepta cada mensaje y activa tripwire si detecta insultos o contenido ofensivo.
- `wingfoil_agent` incluye `input_guardrails=[inappropriate_guardrail]`, garantizando validación previa a la respuesta.
- En el endpoint `chat_api`, se captura `InputGuardrailTripwireTriggered` y devuelve un mensaje estándar de bloqueo al usuario.
- Proporciona un manejo de excepciones uniforme y profesional ante contenido ofensivo.

### **Summary of Interaction**
- **`run.py`** starts the app and ensures the DB is ready.
- **`app.py`** is the core, wiring together routes, database, and chatbot logic.
- **`models.py`** provides the data structure and ORM for all persistent data.
- **`agent.py`** now handles all AI-related queries via the OpenAI Agents SDK and is invoked by its blueprint registered in `app.py`.

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