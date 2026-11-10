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

@app.route('/hablar/<mensaje>', methods=['GET'])
def hablar(mensaje):
    """Envía un mensaje a Groq y genera su voz HD con ElevenLabs."""
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
            # Aquí puedes conectar luego una API del clima si lo deseas; por ahora le damos un contexto base
            contexto_extra = f"[Información del sistema: Los sistemas meteorológicos indican condiciones estables para el día de hoy]."

        # Preparar prompt del sistema con el contexto adicional si aplica
        prompt_sistema = "Eres Visión, un asistente virtual avanzado, sofisticado y elegante al estilo de JARVIS. Responde de forma breve, distinguida y natural."
        if contexto_extra:
            prompt_sistema += f" Ten en cuenta este dato para responder: {contexto_extra}"

        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": prompt_sistema
                },
                {
                    "role": "user",
                    "content": mensaje
                }
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        texto_respuesta = completion.choices[0].message.content
        print(f"<-- Respuesta de Groq: {texto_respuesta}")
        
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