import asyncio
import os
from flask import Blueprint, request, jsonify, session
from agents import (
    Agent,
    Runner,
    input_guardrail,
    GuardrailFunctionOutput,
    RunContextWrapper,
    InputGuardrailTripwireTriggered,
    function_tool,
)
from pydantic import BaseModel, ConfigDict
from models import db, User, Session, ChatMessage, insert_message, fetch_history
from dotenv import load_dotenv
import json
from uuid import uuid4

load_dotenv()

agent_bp = Blueprint('agent', __name__, url_prefix='/agent')

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("ADVERTENCIA CRÍTICA: La variable de entorno OPENAI_API_KEY no está configurada. El chatbot no funcionará.")

# Guardrail output model
class GuardrailOutput(BaseModel):
    is_inappropriate: bool
    reasoning: str

# Context model to provide user information to the agent
class UserProfile(BaseModel):
    id: int
    username: str
    name: str | None = None
    nationality: str | None = None
    age: int | None = None
    sports_practiced: str | None = None
    location: str | None = None
    wingfoil_level: str | None = None
    wingfoiling_since: str | None = None

    model_config = ConfigDict(from_attributes=True)

# Guardrail agent
guardrail_agent = Agent(
    name="Inappropriate Language Guardrail",
    instructions="Valida si el mensaje contiene lenguaje inapropiado. is_inappropriate=True solo si es ofensivo. Explica en 'reasoning'.",
    output_type=GuardrailOutput,
    model="gpt-4o"
)

# Decorated guardrail function
@input_guardrail
async def inappropriate_guardrail(ctx: RunContextWrapper[None], agent, user_input: str) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, user_input, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_inappropriate
    )

# Context injection helper
def generate_instructions(wrapper: RunContextWrapper[UserProfile | None], agent: Agent[UserProfile]) -> str:
    """Genera instrucciones dinámicas basadas en ``UserProfile`` suministrado."""
    profile = wrapper.context
    if not profile:
        return (
            "Eres un asistente de wingfoil que se encarga de apoyar y motivar a los usuarios de nuestra plataforma para que continuen tomando clases y logueando sus sesiones."
        )
    parts = []
    if profile.name:
        parts.append(f"Nombre: {profile.name}")
    if profile.nationality:
        parts.append(f"Nacionalidad: {profile.nationality}")
    if profile.age is not None:
        parts.append(f"Edad: {profile.age}")
    if profile.location:
        parts.append(f"Localización: {profile.location}")
    if profile.sports_practiced:
        parts.append(f"Deportes: {profile.sports_practiced}")
    if profile.wingfoiling_since:
        parts.append(f"Wingfoiling desde: {profile.wingfoiling_since}")
    if profile.wingfoil_level:
        parts.append(f"Nivel: {profile.wingfoil_level}")
    summary = " | ".join(parts)
    base = (
        "Eres un asistente de wingfoil que se encarga de apoyar y motivar a los usuarios de nuestra plataforma para que continuen tomando clases y logueando sus sesiones."
        "Tratas a los usuarios de manera personal, amigable basandote en su perfil e historia de sesiones."
    
    )
    return base + (f"Perfil del usuario: {summary}" if summary else "")

@function_tool
async def fetch_extra_profile(ctx: RunContextWrapper[UserProfile], field: str) -> str:
    """Optional tool to fetch extra user data fields."""
    value = getattr(ctx.context, field, None)
    return str(value) if value is not None else "Dato no disponible"

@function_tool
async def fetch_user_sessions(ctx: RunContextWrapper[UserProfile]) -> str:
    """Devuelve un resumen de las últimas sesiones del usuario."""
    user_id = ctx.context.id
    sessions = db.session.query(Session).filter_by(user_id=user_id).order_by(Session.date.desc()).limit(5).all()
    if not sessions:
        return "No hay sesiones registradas."
    # Devuelve campos específicos de las sesiones en formato JSON
    session_list = []
    for s in sessions:
        session_list.append({
            "date": s.date,
            "sport_type": s.sport_type,
            "duration": s.duration,
            "rating": s.rating,
            "location": s.location,
            "notes": s.notes,
            "achievements": s.achievements,
            "challenges": s.challenges,
            "conditions": s.conditions,
            "instructor_feedback": s.instructor_feedback
        })
    return json.dumps(session_list, ensure_ascii=False)

# Definición del Agente con instrucciones dinámicas y herramientas
try:
    wingfoil_agent = Agent[UserProfile](
        name="InstructorWingfoil",
        model="gpt-4o",
        instructions=generate_instructions,
        input_guardrails=[inappropriate_guardrail],
        tools=[fetch_extra_profile, fetch_user_sessions]
    )
except Exception as e:
    print(f"Error al inicializar el Agente: {e}")
    wingfoil_agent = None


@agent_bp.route('/api/chat', methods=['POST'])
def chat_api():
    if not wingfoil_agent:
        return jsonify({"error": "El agente del chatbot no está inicializado correctamente."}), 500
    
    if not OPENAI_API_KEY: 
        return jsonify({"error": "Configuración de API Key faltante en el servidor."}), 500

    # 1. Recibir mensaje del usuario y session_id
    user_message = request.json.get('message', '')
    session_id = request.json.get('session_id')  # Frontend debe enviar esto
    user_id = session.get('user_id')
    
    # Si no hay session_id, generar uno nuevo
    if not session_id:
        session_id = str(uuid4())
    
    # Greeting inicial cuando el widget se abre (mensaje vacío)
    if not user_message:
        user_profile = None
        if user_id:
            user = db.session.query(User).filter_by(id=user_id).first()
            if user:
                user_profile = UserProfile(
                    id=user.id,
                    username=user.username,
                    name=user.name,
                    nationality=user.nationality,
                    age=user.age,
                    sports_practiced=user.sports_practiced,
                    location=user.location,
                    wingfoil_level=user.wingfoil_level,
                    wingfoiling_since=user.wingfoiling_since,
                )
        if user_profile and user_profile.name:
            greeting = f"¡Hola {user_profile.name}! ¿En qué puedo ayudarte hoy?"
        else:
            greeting = "¡Hola! Bienvenido al asistente de Wingfoil. ¿En qué puedo ayudarte hoy?"
        return jsonify({"reply": greeting, "session_id": session_id}), 200

    # 2. Guardar mensaje del usuario en BD
    insert_message(session_id, "user", user_message, user_id)

    # 3. Preparar contexto del usuario
    user_profile = None
    if user_id:
        user = db.session.query(User).filter_by(id=user_id).first()
        if user:
            user_profile = UserProfile(
                id=user.id,
                username=user.username,
                name=user.name,
                nationality=user.nationality,
                age=user.age,
                sports_practiced=user.sports_practiced,
                location=user.location,
                wingfoil_level=user.wingfoil_level,
                wingfoiling_since=user.wingfoiling_since,
            )
    
    try:
        # 4. Enviar mensaje al agente IA
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop = asyncio.get_event_loop()
        
        result = loop.run_until_complete(
            Runner.run(wingfoil_agent, user_message, context=user_profile)
        )
        
        if hasattr(result, 'final_output') and result.final_output is not None:
            response_text = result.final_output
        else:
            print(f"Advertencia: El objeto resultado no tiene 'final_output' o es None. Contenido: {result}")
            response_text = "No se pudo obtener una respuesta clara del agente."
            if hasattr(result, 'history') and result.history: 
                last_event = result.history[-1]
                if hasattr(last_event, 'content'):
                    response_text = str(last_event.content) 
                else:
                    response_text = str(last_event)

        # 5. Guardar respuesta del agente
        insert_message(session_id, "assistant", response_text, user_id)

        # 6. Retornar respuesta al usuario con session_id
        return jsonify({"reply": response_text, "session_id": session_id})

    except InputGuardrailTripwireTriggered:
        return jsonify({"reply": "Mensaje bloqueado por lenguaje inapropiado.", "session_id": session_id}), 200
    except Exception as e:
        error_message_for_log = f"Error en la ejecución del agente: {type(e).__name__} - {str(e)}"
        print(error_message_for_log)
        return jsonify({"error": "Ocurrió un error al procesar tu mensaje.", "session_id": session_id}), 500


@agent_bp.route('/history', methods=['GET'])
def chat_history():
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({"error": "session_id parameter required"}), 400
    
    # Opcional: verificar que el usuario tenga acceso a esta sesión
    user_id = session.get('user_id')
    if user_id:
        # Verificar que al menos un mensaje de la sesión pertenezca al usuario actual
        user_message_exists = ChatMessage.query.filter_by(
            session_id=session_id, 
            user_id=user_id
        ).first()
        if not user_message_exists:
            return jsonify({"error": "Access denied to this conversation session"}), 403
    
    # Usar la función helper para obtener el historial
    messages = fetch_history(session_id)
    return jsonify({"messages": messages, "session_id": session_id})

# Para probar este archivo directamente (opcional, si no lo registras en una app principal)
# if __name__ == '__main__':
#     from flask import Flask
#     app = Flask(__name__)
#     app.secret_key = os.urandom(24) # Necesario para sessiones si las usaras
#     app.register_blueprint(agent_bp)
#     app.run(debug=True, port=5001) # Usar un puerto diferente si tu app principal usa 5000
