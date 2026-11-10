from core.cliente import obtener_cliente

def main():
    print("Inicializando asistente Visión...")
    client = obtener_cliente()
    
    # Prueba rápida de conexión con el modelo estable actual
    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents="Hola, soy Visión, listo para operar.",
    )
    
    print("\n--- Estado del Asistente ---")
    print(response.text)

if __name__ == "__main__":
    main()