import os
import asyncio
from flask import Blueprint, request, jsonify
from agents import Agent, Runner, input_guardrail, GuardrailFunctionOutput, RunContextWrapper, InputGuardrailTripwireTriggered
from pydantic import BaseModel
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

# Definición del Agente
try:
    wingfoil_agent = Agent(
        name="InstructorWingfoil",
        instructions=(
            "Eres un instructor experto en wingfoil. "
            "Proporciona consejos prácticos y motivacionales para principiantes. "
            "Responde de manera amigable y accesible, con respuestas concisas de máximo 300 caracteres."
        ),
        model="gpt-4o",
        input_guardrails=[inappropriate_guardrail]
    )
except Exception as e:
    print(f"Error al inicializar el Agente: {e}. Asegúrate de que la librería 'openai-agents' está instalada y OPENAI_API_KEY es válida.")
    wingfoil_agent = None


@agent_bp.route('/api/chat', methods=['POST'])
def chat_api():
    if not wingfoil_agent:
        return jsonify({"error": "El agente del chatbot no está inicializado correctamente."}), 500
    
    if not OPENAI_API_KEY: 
        return jsonify({"error": "Configuración de API Key faltante en el servidor."}), 500

    user_message = request.json.get('message', '') 
    if not user_message:
        return jsonify({"error": "El campo 'message' es requerido en el JSON."}), 400
    
    try:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop = asyncio.get_event_loop()
        result = loop.run_until_complete(Runner.run(wingfoil_agent, user_message))
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
