import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
from google import genai

# Pega aquí tu clave activa (la que empieza por AQ... o AIzaSy...)


client = genai.Client()

print("Enviando consulta de prueba a Gemini...")

response = client.models.generate_content(
    model='gemini-3.8-flash',  # <--- Cambiado al modelo recomendado actual
    contents="Hola, preséntate brevemente y dime qué eres.",
)

print("\n--- Respuesta del Asistente ---")
print(response.text)