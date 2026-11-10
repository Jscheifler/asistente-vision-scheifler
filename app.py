import os
from flask import Flask, render_template, jsonify
from groq import Groq

app = Flask(__name__)

# Lee la clave de forma segura desde las variables de entorno del sistema
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hablar/<mensaje>', methods=['GET'])
def hablar(mensaje):
    """Envía un mensaje a Groq con respuesta instantánea."""
    try:
        print(f"--> Mensaje enviado a Groq: {mensaje}")
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "Eres Visión, un asistente virtual con cara visual en pantalla. Responde de forma muy breve, amigable y natural."
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
        
        emocion = "neutral"
        if "feliz" in texto_respuesta.lower() or "¡" in texto_respuesta:
            emocion = "happy"
        elif "gracias" in texto_respuesta.lower() or "ayudar" in texto_respuesta.lower():
            emocion = "happy"

        return jsonify({
            "status": "success",
            "respuesta": texto_respuesta,
            "emocion": emocion
        })
        
    except Exception as e:
        print(f"[ERROR CON GROQ]: {e}")
        return jsonify({
            "status": "error",
            "mensaje": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)