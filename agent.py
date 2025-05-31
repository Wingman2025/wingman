import os
from flask import Blueprint, request, jsonify
# Asegúrate de que el nombre del paquete sea correcto para la instalación pip
# y que estas sean las clases correctas de la librería.
from agents import Agent, Runner 
# No necesitaríamos RunConfig si solo lo usábamos para el modelo
# from agents.config import RunConfig 
from dotenv import load_dotenv

# Cargar variables de entorno (si tienes un .env para OPENAI_API_KEY)
load_dotenv()

# Cambia 'agent_bp' si prefieres otro nombre para el blueprint
agent_bp = Blueprint('agent', __name__, url_prefix='/agent') # Nuevo nombre de blueprint y prefijo

# Verificar y cargar la API Key de OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("ADVERTENCIA CRÍTICA: La variable de entorno OPENAI_API_KEY no está configurada. El chatbot no funcionará.")

# Definición del Agente
try:
    wingfoil_agent = Agent(
        name="InstructorWingfoil",
        instructions=(
            "Eres un instructor experto en wingfoil. "
            "Proporciona consejos prácticos y motivacionales para principiantes. "
            "Responde de manera amigable y accesible, con respuestas concisas de máximo 300 caracteres."
        ),
        model="gpt-4o" # Especificando el modelo directamente aquí
    )
except Exception as e:
    print(f"Error al inicializar el Agente: {e}. Asegúrate de que la librería 'openai-agents' está instalada y OPENAI_API_KEY es válida.")
    wingfoil_agent = None


@agent_bp.route('/api/chat', methods=['POST']) # Ruta dentro del blueprint
def chat_api():
    if not wingfoil_agent:
        return jsonify({"error": "El agente del chatbot no está inicializado correctamente."}), 500
    
    if not OPENAI_API_KEY: 
        return jsonify({"error": "Configuración de API Key faltante en el servidor."}), 500

    user_message = request.json.get('message', '') 
    if not user_message:
        return jsonify({"error": "El campo 'message' es requerido en el JSON."}), 400
    
    try:
        result = Runner.run_sync(
            agent=wingfoil_agent, 
            input=user_message
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
