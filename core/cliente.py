import os
from google import genai
import config

def obtener_cliente():
    """Inicializa el cliente de Gemini priorizando la API Key o la Cuenta de Servicio."""
    # 1. Verificar si hay una API Key en el entorno (ej. exportada en Termux)
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    
    # 2. Si no hay API Key directa, intentamos usar el archivo credentials.json
    credentials_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "credentials.json"))
    if os.path.exists(credentials_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

    # 3. Inicialización estándar utilizando las credenciales detectadas en el entorno
    return genai.Client()