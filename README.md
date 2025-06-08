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
- **AI Chatbot**: Interact with an AI Wingfoil instructor powered by OpenAI Agents (GPT-4o).

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. **Export your OpenAI API key** so the chatbot can connect to the API. You can
   set it in your environment or create a `.env` file containing:
   ```
   OPENAI_API_KEY=your-key-here
   ```
   Then load the file (e.g., with `source .env`) before running the app.

3. Run the application:
   ```
   python run.py
   ```

   ```
   http://127.0.0.1:5000
   ```

## Structure

- `app.py` - Main application file containing all routes and database logic
- `agent.py` - Handles the AI chatbot logic using OpenAI Agents SDK.
- `run.py` - Script to run the application
- `templates/` - HTML templates
- `static/` - Static assets (CSS, JavaScript)
- `wingfoil.db` - SQLite database (created automatically on first run)
- `chatbot.py` - (Obsolete) Previous chatbot implementation.

## Dependencies

- Flask 2.0.1
- Werkzeug 2.0.1
- Jinja2 3.0.1
- Other dependencies listed in requirements.txt

## Chatbot Context

When a user is logged in, the chat endpoint builds a `UserProfile` from the
database and passes it as the `context` to `Runner.run`. The helper
`inject_user_profile` appends a short summary of that profile to the agent's
instructions so responses can be personalized.

Example snippet:

```python
user = db.session.query(User).first()
profile = UserProfile.from_orm(user)
Runner.run(wingfoil_agent, "Hola", context=profile)
```



## Conversation Sessions
The chat API uses a `session_id` to keep track of each conversation. If the
frontend does not send one, `agent.py` generates a new UUID and returns it
alongside the reply. Store this value (for example in `localStorage`) and send it
back with every call to `/agent/api/chat` so the assistant can recall the
conversation.

To fetch the messages of a conversation you can call:

```
GET /agent/history?session_id=<uuid>
```

The endpoint requires the `session_id` query parameter and returns a list of
messages plus the same session ID.

