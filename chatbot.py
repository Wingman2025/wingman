import os
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializar el cliente de OpenAI
client = OpenAI()  # No es necesario especificar api_key si está en la variable de entorno OPENAI_API_KEY

def ask_wingfoil_ai(question):
    """
    Función para interactuar con el modelo de OpenAI y obtener respuestas
    relacionadas con wingfoil.
    
    Args:
        question (str): La pregunta o consulta del usuario
        
    Returns:
        str: La respuesta generada por el modelo
    """
    # Definir instrucciones personalizadas detalladas
    instructions = (
        "Eres un asistente experto en wingfoil. "
        "Proporciona respuestas precisas y detalladas sobre técnicas, equipos y seguridad. "
        "Comunícate de manera amigable y accesible para principiantes, "
        "pero también ofrece información avanzada para usuarios experimentados. "
        "Si es relevante, incluye consejos prácticos y recursos adicionales."
     )
    # Llamar a la API de OpenAI usando el método responses.create
    response = client.responses.create(
        model="gpt-4o",  # Ajusta el modelo si es necesario
        instructions=instructions,
        input=question
    )
    
    # Extraer y devolver la respuesta
    return response.output_text
