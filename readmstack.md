# Wingman Project Technology Stack

The Wingman project leverages a robust and modern technology stack to deliver a scalable, secure, and intelligent web application experience. Below is a summary of the core technologies and services used:

## Table of Contents
- [Backend](#backend)
- [Frontend](#frontend)
- [AI & Chatbot](#ai--chatbot)
- [Testing the Agent Locally with cURL](#testing-the-agent-locally-with-curl)
- [Deployment & Infrastructure](#deployment--infrastructure)
- [Additional Libraries & Tools](#additional-libraries--tools)
- [Security & Best Practices](#security--best-practices)
- [Process Flow & File Interactions](#process-flow--file-interactions)
- [Admin Functionality & Management](#admin-functionality--management)
- [Chat History Persistence Implementation](#chat-history-persistence-implementation)

## Backend
- **Python**: Primary programming language for backend logic.
- **Flask**: Lightweight web framework used to build the API and serve web pages.
- **WSGI (Web Server Gateway Interface)**: Used for running the Flask app in production environments.
- **PostgreSQL**: Relational database for storing user data, skills, sessions, and application state. Used both in local development and production (Railway).
- **AWS S3**: Used in production for storing uploaded images and other media. `app.py` configures the `S3_KEY`, `S3_SECRET`, `S3_REGION` and `S3_BUCKET` variables and provides the `upload_file_to_s3` helper that relies on `boto3` to push files to the bucket.

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
- **Purpose:** Context-aware chatbot usando el `openai-agents-python` SDK.
- **Key Components:**
  - `UserProfile` (Pydantic) traslada datos del usuario desde la BD.
  - `generate_instructions(wrapper)` genera prompts dinámicos por usuario.
  - `fetch_extra_profile` como tool para datos adicionales bajo demanda.
  - `fetch_user_sessions` como tool para obtener las últimas 5 sesiones de un usuario.
  - `inappropriate_guardrail` en `input_guardrails` filtra lenguaje ofensivo.
  - Agente definido como:
    ```python
    Agent[UserProfile](
      name="InstructorWingfoil",
      model="gpt-4o",
      instructions=generate_instructions,
      tools=[fetch_extra_profile, fetch_user_sessions],
      input_guardrails=[inappropriate_guardrail]
    )
    ```
- **Flow (detalle):**
  1. POST a `/agent/api/chat`:  
     - `data = request.get_json(silent=True) or {}`  
     - `user_message = data.get('message','')` → 400 si está vacío.  
  2. Autenticación y carga de perfil:  
     - `user_id = session.get('user_id')`;  
     - Carga `User` con SQLAlchemy;  
     - Construye `UserProfile` (Pydantic con `from_attributes=True`) con campos:  
       `id, username, name, nationality, age, sports_practiced, location, wingfoil_level, wingfoiling_since`.  
  3. Preparación del loop asyncio:  
     - Intenta `loop = asyncio.get_event_loop()`;  
     - Si lanza `RuntimeError`, usa `loop = asyncio.new_event_loop()` y `asyncio.set_event_loop(loop)`.  
  4. Llamada al agente:  
     ```python
     result = loop.run_until_complete(
         Runner.run(
             wingfoil_agent,
             user_message,
             context=user_profile
         )
     )
     ```  
     - El SDK invoca `generate_instructions(wrapper, agent)` para armar el prompt con contexto.  
     - Aplica el guardrail `inappropriate_guardrail`.  
     - Tools (`fetch_extra_profile`, `fetch_user_sessions`) disponibles para llamadas de modelo.  
  5. Procesamiento de respuesta:  
     - Si `result.final_output` existe, se usa como `reply`;  
     - Sino, extrae `result.history[-1].content`;  
     - Sino, retorna mensaje de fallback.  
  6. Manejo de errores:  
     - `InputGuardrailTripwireTriggered` → responde 200 con `{ "reply": "Mensaje bloqueado por lenguaje inapropiado." }`;  
     - Otra excepción → log en consola y responde 500 con `{ "error": "Ocurrió un error al procesar tu mensaje." }`.

### Guardrail LLM (Filtro de Lenguaje)
- Mantiene `inappropriate_guardrail` para bloquear únicamente lenguaje inapropiado.

### **Tool adicional `fetch_user_sessions`:**
- Firma: `async def fetch_user_sessions(ctx: RunContextWrapper[UserProfile]) -> str`
- Obtiene las últimas 5 sesiones de `Session` desde la BD y retorna un resumen: fecha, deporte, duración y rating.
- Útil para que el agente extraiga del historial de usuario y contextualice consejos basados en su progreso reciente.

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

## Chat History Persistence Implementation

### Overview
Implementamos un sistema de persistencia de historial de chat basado en sesiones que permite al chatbot mantener contexto conversacional dentro de cada sesión de usuario, evitando cargar todo el historial histórico.

### Arquitectura de Sesiones

#### Session ID Management
- **Generación**: Se genera un UUID único (`session_id`) para cada nueva conversación
- **Persistencia**: El `session_id` se pasa entre frontend y backend para mantener continuidad
- **Alcance**: Cada sesión mantiene su propio historial independiente

#### Database Schema
```sql
-- Tabla chat_message extendida con session_id
CREATE TABLE chat_message (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    sender VARCHAR(10) NOT NULL,  -- 'user' o 'assistant'
    message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(36),  -- UUID de la sesión
    FOREIGN KEY (user_id) REFERENCES user (id)
);
```

### Helper Functions (models.py)

#### `insert_message(session_id, sender, message, user_id=None)`
- Inserta mensajes en la base de datos con el `session_id` asociado
- Maneja tanto mensajes de usuario como respuestas del asistente

#### `fetch_history(session_id)`
- Recupera todos los mensajes de una sesión específica ordenados por timestamp
- Retorna lista de diccionarios con estructura: `{id, sender, message, timestamp}`

#### `format_history_for_context(session_id)`
- Formatea el historial como string para pasar como contexto al agente OpenAI
- Formato: `"user: mensaje\nassistant: respuesta\n..."`

### API Endpoints

#### `/api/chat` (POST)
**Request:**
```json
{
    "message": "Hola, ¿cómo estás?",
    "session_id": "optional-uuid-v4"  // Si no se provee, se genera uno nuevo
}
```

**Response:**
```json
{
    "reply": "¡Hola! Estoy bien, gracias por preguntar.",
    "session_id": "generated-or-provided-uuid"
}
```

**Flujo:**
1. Recibe mensaje y `session_id` (o genera uno nuevo)
2. Guarda mensaje del usuario con `session_id`
3. Recupera historial de la sesión actual
4. Construye `ConversationContext` con perfil de usuario e historial
5. Invoca agente OpenAI con contexto completo
6. Guarda respuesta del asistente con mismo `session_id`
7. Retorna respuesta y `session_id`

#### `/history` (GET)
**Parameters:**
- `session_id`: UUID de la sesión a consultar

**Response:**
```json
[
    {
        "id": 1,
        "sender": "user",
        "message": "Hola",
        "timestamp": "2025-06-08T00:15:30"
    },
    {
        "id": 2,
        "sender": "assistant", 
        "message": "¡Hola! ¿En qué puedo ayudarte?",
        "timestamp": "2025-06-08T00:15:32"
    }
]
```

### Context Model

#### ConversationContext (Pydantic)
```python
class ConversationContext(BaseModel):
    user_profile: UserProfile | None
    conversation_history: str  # String-based context
```

**Context Passing to OpenAI Agent:**
El contexto se pasa al agente OpenAI como un string formateado que incluye:
1. **Perfil del Usuario**: Información relevante del usuario (nombre, nivel, experiencia)
2. **Historial de Conversación**: Mensajes previos de la sesión actual
3. **Mensaje Actual**: El mensaje que el usuario acaba de enviar

**Formato del Contexto:**
```
Usuario: [nombre/username/Visitante (no autenticado)]
Nacionalidad: [nacionalidad]  # Solo si está disponible
Edad: [edad]  # Solo si está disponible
Nivel de wingfoil: [nivel]  # Solo si está disponible
Practica wingfoil desde: [fecha]  # Solo si está disponible

Historial de conversación:
user: mensaje anterior
assistant: respuesta anterior

Mensaje actual: [mensaje del usuario]
```

### Migration Strategy

#### Database Migration
```bash
# Generar migración
python -m flask --app run.py db migrate -m "add session_id to chat_message"

# Aplicar migración
python -m flask --app run.py db upgrade

# En caso de conflictos, marcar como aplicada
python -m flask --app run.py db stamp <revision_id>
```

### Benefits

1. **Contexto Sesión-Específico**: El agente solo ve el historial relevante de la conversación actual
2. **Escalabilidad**: Evita cargar miles de mensajes históricos en cada request
3. **Múltiples Sesiones**: Los usuarios pueden tener múltiples conversaciones concurrentes
4. **Stateless Backend**: El servidor no mantiene estado entre requests
5. **Seguridad**: Los usuarios solo pueden acceder al historial de sesiones donde tienen mensajes

### Frontend Integration Requirements

El frontend debe:
1. Generar/persistir `session_id` (localStorage, sessionStorage, o estado de aplicación)
2. Enviar `session_id` en cada request a `/api/chat`
3. Manejar `session_id` retornado para nuevas sesiones
4. Implementar UI para múltiples sesiones si es necesario

### Production Considerations

- **Token Optimization**: Considerar límites de longitud de historial para optimizar uso de tokens
- **Data Retention**: Implementar políticas de limpieza de sesiones antiguas
- **Indexing**: Agregar índices en `session_id` para queries eficientes
- **Monitoring**: Trackear métricas de sesiones activas y longitud promedio de conversaciones
