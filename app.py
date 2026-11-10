import os
import datetime
import requests
from flask import Flask, render_template, jsonify
from groq import Groq

app = Flask(__name__)

# Lee la clave de Groq de forma segura desde las variables de entorno
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Lee la clave de ElevenLabs desde las variables de entorno
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")

# ID de voz estilo JARVIS (George - Cálido, británico y elegante)
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"

# Historial de conversación para mantener la memoria del chat
historial_conversacion = [
    {
        "role": "system",
        "content": "Eres Visión, un asistente virtual avanzado, sofisticado y elegante al estilo de JARVIS. Responde de forma breve, distinguida y natural."
    }
]

@app.route('/')
def index():
    return render_template('index.html')

def generar_voz_elevenlabs(texto):
    """Envía el texto a la API de ElevenLabs y guarda el archivo mp3 resultante."""
    if not ELEVENLABS_API_KEY:
        print("[ADVERTENCIA]: ELEVENLABS_API_KEY no está configurada en las variables de entorno.")
        return None
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": texto,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.85
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            audio_path = os.path.join("static", "audio_respuesta.mp3")
            with open(audio_path, "wb") as f:
                f.write(response.content)
            return "/static/audio_respuesta.mp3"
        else:
            print(f"[ERROR ELEVENLABS]: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"[EXCEPCIÓN ELEVENLABS]: {e}")
        return None

def obtener_clima():
    """Consulta el clima actual en tiempo real de forma gratuita."""
    try:
        response = requests.get("https://wttr.in/?format=3", timeout=5)
        if response.status_code == 200:
            return response.text.strip()
    except Exception as e:
        print(f"[ERROR CLIMA]: {e}")
    return "condiciones estables"

@app.route('/hablar/<mensaje>', methods=['GET'])
def hablar(mensaje):
    """Envía un mensaje a Groq con memoria de chat y genera su voz HD con ElevenLabs."""
    global historial_conversacion
    try:
        print(f"--> Mensaje enviado a Groq: {mensaje}")
        mensaje_lower = mensaje.lower()
        
        # --- HERRAMIENTAS LOCALES (HORA, FECHA, CLIMA) ---
        contexto_extra = ""
        now = datetime.datetime.now()
        
        if "hora" in mensaje_lower:
            hora_actual = now.strftime("%H:%M")
            contexto_extra = f"[Información del sistema: La hora actual es {hora_actual}]."
        elif "fecha" in mensaje_lower or "día" in mensaje_lower:
            fecha_actual = now.strftime("%A, %d de %B de %Y")
            contexto_extra = f"[Información del sistema: La fecha de hoy es {fecha_actual}]."
        elif "clima" in mensaje_lower or "tiempo" in mensaje_lower:
            clima_actual = obtener_clima()
            contexto_extra = f"[Información del sistema: El reporte meteorológico actual es {clima_actual}]."

        # Creamos una lista temporal para enviar el historial más el nuevo mensaje y contexto
        mensajes_para_enviar = list(historial_conversacion)
        
        if contexto_extra:
            mensajes_para_enviar.append({
                "role": "system",
                "content": contexto_extra
            })

        mensajes_para_enviar.append({
            "role": "user",
            "content": mensaje
        })

        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=mensajes_para_enviar,
            temperature=0.7,
            max_tokens=150
        )
        
        texto_respuesta = completion.choices[0].message.content
        print(f"<-- Respuesta de Groq: {texto_respuesta}")
        
        # Guardamos el intercambio en la memoria permanente del servidor
        historial_conversacion.append({"role": "user", "content": mensaje})
        historial_conversacion.append({"role": "assistant", "content": texto_respuesta})
        
        # Opcional: Limitar el historial para evitar desbordar el límite de tokens (mantiene el prompt de sistema + últimos 20 mensajes)
        if len(historial_conversacion) > 21:
            historial_conversacion = [historial_conversacion[0]] + historial_conversacion[-20:]

        # Determinación de estados emocionales para la interfaz visual
        emocion = "neutral"
        texto_lower = texto_respuesta.lower()
        if any(w in texto_lower for w in ["feliz", "excelente", "un placer", "gracias", "listo", "¡"]):
            emocion = "happy"
        elif any(w in texto_lower for w in ["procesando", "analizando", "pensando", "comprobando"]):
            emocion = "thinking"

        # Generar la voz ultrarrealista de ElevenLabs
        audio_url = generar_voz_elevenlabs(texto_respuesta)

        return jsonify({
            "status": "success",
            "respuesta": texto_respuesta,
            "emocion": emocion,
            "audio_url": audio_url
        })
        
    except Exception as e:
        print(f"[ERROR CON GROQ]: {e}")
        return jsonify({
            "status": "error",
            "mensaje": str(e)
        }), 500

if __name__ == '__main__':
    os.makedirs("static", exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)