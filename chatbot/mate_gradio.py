import os
import uuid
from gtts import gTTS
from playsound import playsound
import gradio as gr
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

from chatbot.memoria_db import crear_base, guardar_interaccion, obtener_historial
from chatbot.conexion_postgres import obtener_conexion

# Inicializar la base de datos de memoria
crear_base()

# Cargar variables de entorno
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

# 🎙️ Nueva función de voz usando gTTS
def hablar(texto):
    try:
        tts = gTTS(text=texto, lang='es', tld='com.mx')  # Puedes cambiar tld a 'com', 'com.ar', etc.
        nombre_audio = f"mate_{uuid.uuid4().hex}.mp3"
        tts.save(nombre_audio)
        playsound(nombre_audio)
        os.remove(nombre_audio)
    except Exception as e:
        print("❌ Error al reproducir audio:", e)

# Inicializar modelo de lenguaje con memoria
llm = ChatOpenAI(
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=api_key,
    model="openai/gpt-3.5-turbo",
    temperature=0.7
)
memoria = ConversationBufferMemory()
chatbot = ConversationChain(llm=llm, memory=memoria)

# ID de empresa simulada
empresa_id = "empresa_001"

# Consulta real a clientes en Supabase
def contar_clientes_activos(empresa_id):
    try:
        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM clientes
            WHERE empresa_id = %s AND activo = TRUE
        """, (empresa_id,))
        total = cur.fetchone()[0]
        conn.close()
        return total
    except Exception as e:
        return f"Error al consultar la base de datos: {e}"

# Función principal que responde
def responder(mensaje):
    historial = obtener_historial(empresa_id)

    for msg, resp in historial:
        chatbot.memory.chat_memory.add_user_message(msg)
        chatbot.memory.chat_memory.add_ai_message(resp)

    # Intercepción por intención básica
    if "clientes activos" in mensaje.lower():
        total = contar_clientes_activos(empresa_id)
        respuesta = f"Tienes {total} clientes activos registrados en el CRM."
    else:
        respuesta = chatbot.run(mensaje)

    guardar_interaccion(empresa_id, mensaje, respuesta)
    hablar(respuesta)
    return respuesta

# Interfaz Gradio
iface = gr.Interface(
    fn=responder,
    inputs=gr.Textbox(lines=2, placeholder="Escribe o pega aquí tu mensaje..."),
    outputs="text",
    title="Mate - Tu copiloto PyMate",
    description="Mate responde por voz y texto. Pregunta sobre tus clientes, finanzas y más."
)

iface.launch()
