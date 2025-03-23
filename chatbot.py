from flask import Flask, request, jsonify, render_template
import os
import base64
from openai import OpenAI
from dotenv import load_dotenv
import tempfile

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
client = OpenAI()

# Variable global para mantener el ID de la respuesta anterior
current_response_id = None

def encode_image(image_path):
    """Función para codificar una imagen en base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def ask_wingfoil_ai(question, image_path=None):
    """Función para interactuar con el modelo de OpenAI"""
    global current_response_id
    
    instructions = (
        "Comunícate de manera amigable y accesible para principiantes, "
        "incluye consejos prácticos y recursos adicionales como tecnicas para aprender para que las personas se motiven en aprender "
        "Cuando hagas las recomendaciones de utilizar los servicios de la web, utiliza frases como 'nuestra web',"
        "Si te preguntan por el tiempo prioriza buscar en la pagina web de windguru.cz y da respuestas especificas y concretas asociadas a la navegacion con wingfoil para el dia actual,"
        "Si te envían una imagen relacionada con el wingfoil, analízala y proporciona comentarios sobre la técnica, equipo o condiciones que ves en ella,"
        "Si la imagen no tiene nada que ver con el wingfoil, di que no es una imagen relacionada con el wingfoil"
        "Proporciona respuestas concisas de máximo 300 caracteres,"
    )
    
    # Preparar el contenido de la consulta
    content = []
    
    # Agregar texto
    content.append({"type": "input_text", "text": question})
    
    # Agregar imagen si se proporciona
    if image_path:
        # Verificar si es una URL o un archivo local
        if image_path.startswith(('http://', 'https://')):
            content.append({
                "type": "input_image",
                "image_url": image_path,
                "detail": "high"
            })
        else:
            # Es un archivo local, codificar en base64
            base64_image = encode_image(image_path)
            content.append({
                "type": "input_image",
                "image_url": f"data:image/jpeg;base64,{base64_image}",
                "detail": "high"
            })
    
    # Llamar a la API de OpenAI
    response = client.responses.create(
        model="gpt-4o",
        tools=[{
            "type": "web_search_preview",
            "user_location": {
                "type": "approximate",
                "country": "ES",
                "city": "Tarifa",   
                "region": "Cadiz",
            }
        }],
        instructions=instructions,
        input=[
            {"role": "system", "content": "Eres un instructor experto en wingfoil, das consejos y recomendaciones para los usuario y recomiendas utilizar los servicios de la web de wingman para definir objetivos y llevar un roadmap de aprendizaje."},
            {"role": "developer", "content": instructions},
            {"role": "user", "content": content},
        ],
        previous_response_id=current_response_id
    )
    current_response_id = response.id
    return response.output_text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    # Obtener el mensaje del usuario
    user_message = request.form.get('message', '')
    
    # Comprobar si hay una imagen adjunta
    image_file = None
    if 'image' in request.files:
        image_file = request.files['image']
    
    # Si hay una imagen, guardarla temporalmente
    image_path = None
    if image_file and image_file.filename != '':
        # Crear un archivo temporal
        temp_dir = tempfile.mkdtemp()
        image_path = os.path.join(temp_dir, image_file.filename)
        image_file.save(image_path)
    
    # Llamar a la función para obtener la respuesta
    try:
        response = ask_wingfoil_ai(user_message, image_path)
        
        # Eliminar el archivo temporal si existe
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
            os.rmdir(temp_dir)
        
        return jsonify({"response": response})
    except Exception as e:
        # En caso de error, también limpiar
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
            os.rmdir(temp_dir)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)