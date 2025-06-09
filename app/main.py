from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import google.generativeai as genai
from config import GEMINI_API_KEY
import json

# Configuración de Gemini
genai.configure(api_key=GEMINI_API_KEY)
templates = Jinja2Templates(directory="templates")

app = FastAPI()

# Datos de ejemplo por defecto
datos_financieros = {
    "ingresos": 1800,
    "gastos_totales": 1350,
    "gastos_por_categoria": {
        "comida": 450,
        "transporte": 200,
        "entretenimiento": 300,
        "suscripciones": 100,
        "otros": 300
    }
}

# Generar el prompt personalizado
def generar_prompt_finanzas(datos_financieros):
    ingresos = datos_financieros["ingresos"]
    gastos = datos_financieros["gastos_totales"]
    categorias = datos_financieros["gastos_por_categoria"]
    categorias_str = "\n".join([f"- {k}: ${v}" for k, v in categorias.items()])

    prompt = f"""
Eres un asesor financiero personal con experiencia ayudando a personas a mejorar su economía.
Un usuario te ha compartido sus datos financieros del último mes.

Tu tarea es:
- Analizar si sus gastos están equilibrados respecto a sus ingresos.
- Detectar si gasta más de lo que gana.
- Identificar categorías donde podría ahorrar.
- Sugerir al menos 2 acciones concretas, realistas y fáciles de aplicar para mejorar su situación financiera.
- Explicar tus recomendaciones de forma sencilla, amable y motivadora, como si hablaras con alguien sin conocimientos financieros.

Datos del usuario:
- Ingresos mensuales: ${ingresos}
- Gastos totales: ${gastos}
- Gastos por categoría:
{categorias_str}

Por favor, responde en un solo párrafo breve y claro, usando un lenguaje positivo y práctico.
"""
    return prompt

# Obtener respuesta personalizada a partir de datos financieros
def chat_finanzas_personales(datos_financieros):
    prompt = generar_prompt_finanzas(datos_financieros)
    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(
        [prompt],
        generation_config=genai.types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=512
        )
    )
    return response.text

# Obtener respuesta general para entradas libres
def chat_with_gemini(user_input):
    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(
        [user_input],
        generation_config=genai.types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=512
        )
    )
    return response.text

# Chatbot CLI desde terminal
def start_chatbot():
    print("👋 ¡Hola, soy tu consejero financiero virtual!")
    print("Escribe 'finanzas' para recibir un consejo financiero personalizado.")
    print("Escribe 'bye' para salir.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "bye":
            print("Adiós 👋")
            break
        elif user_input.lower() == "finanzas":
            try:
                respuesta = chat_finanzas_personales(datos_financieros)
                print(f"\n💡 Consejo financiero:\n{respuesta}\n")
            except Exception as e:
                print(f"❌ Error: {str(e)}\n")
        else:
            try:
                response = chat_with_gemini(user_input)
                print(f"🤖 Bot: {response}\n")
            except Exception as e:
                print(f"❌ Error: {str(e)}\n")

# Endpoint POST: análisis financiero personalizado
@app.post("/api/chat/finanzas")
async def chat_finanzas(request: Request):
    try:
        raw = await request.body()
        datos = json.loads(raw.decode("utf-8"))
        respuesta = chat_finanzas_personales(datos)
        return {"response": respuesta}
    except Exception as e:
        return {"error": str(e)}


# Solo para modo consola (terminal)
if __name__ == "__main__":
    start_chatbot()
    # Para levantar como servidor API, comenta arriba y descomenta abajo:
    # import uvicorn
    # uvicorn.run(app, host="127.0.0.1", port=8000)

# Conexión al frontend
# Desde el frontend (JavaScript) un fetch al 
# endpoint correspondiente, y mostrar la respuesta en la interfaz.

# Para múltiples usuarios, pasar su user_id y obtener sus datos personalizados.

# Gemini funciona mejor cuando el prompt es muy claro: cantidades, 
# contexto y lo que se espera que haga.
