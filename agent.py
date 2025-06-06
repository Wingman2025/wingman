import os
import asyncio
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
from models import db, User, Session
from dotenv import load_dotenv

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
def generate_instructions(wrapper: RunContextWrapper[UserProfile], agent: Agent[UserProfile]) -> str:
    """Genera instrucciones dinámicas con perfil de usuario completo."""
    profile = wrapper.context
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
    lines = []
    for s in sessions:
        lines.append(f"{s.date}: {s.sport_type}, {s.duration} min, rating {s.rating}")
    return "\n".join(lines)

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

    user_message = request.json.get('message', '')
    # Greeting inicial cuando el widget se abre (mensaje vacío)
    if not user_message:
        user_profile = None
        user_id = session.get('user_id')
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
        return jsonify({"reply": greeting}), 200

    user_profile = None
    user_id = session.get('user_id')
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

        return jsonify({"reply": response_text})

    except InputGuardrailTripwireTriggered:
        return jsonify({"reply": "Mensaje bloqueado por lenguaje inapropiado."}), 200
    except Exception as e:
        error_message_for_log = f"Error en la ejecución del agente: {type(e).__name__} - {str(e)}"
        print(error_message_for_log) 
        return jsonify({"error": "Ocurrió un error al procesar tu mensaje."}), 500

# Para probar este archivo directamente (opcional, si no lo registras en una app principal)
# if __name__ == '__main__':
#     from flask import Flask
#     app = Flask(__name__)
#     app.secret_key = os.urandom(24) # Necesario para sessiones si las usaras
#     app.register_blueprint(agent_bp)
#     app.run(debug=True, port=5001) # Usar un puerto diferente si tu app principal usa 5000
