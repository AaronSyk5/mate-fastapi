import os
import uuid
from gtts import gTTS
from playsound import playsound
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from dotenv import load_dotenv
import psycopg2

# Cargar variables de entorno
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
db_url = os.getenv("DATABASE_URL")

# Configurar modelo
llm = ChatOpenAI(
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=api_key,
    model="openai/gpt-3.5-turbo",
    temperature=0.7
)

# 🧠 Obtener historial de Supabase (PostgreSQL)
def obtener_historial(empresa_id):
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("""
            SELECT mensaje, respuesta FROM historial_chat
            WHERE empresa_id = %s
            ORDER BY creado_en ASC
            LIMIT 10
        """, (empresa_id,))
        historial = cur.fetchall()
        conn.close()
        return historial
    except Exception as e:
        print("❌ Error al obtener historial:", e)
        return []

# 🧠 Guardar interacción
def guardar_interaccion(empresa_id, mensaje, respuesta):
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO historial_chat (empresa_id, mensaje, respuesta)
            VALUES (%s, %s, %s)
        """, (empresa_id, mensaje, respuesta))
        conn.commit()
        conn.close()
    except Exception as e:
        print("❌ Error al guardar historial:", e)

# 🎙️ Voz natural
def hablar(texto):
    try:
        tts = gTTS(text=texto, lang='es', tld='com.mx')
        nombre_audio = f"mate_{uuid.uuid4().hex}.mp3"
        tts.save(nombre_audio)
        playsound(nombre_audio)
        os.remove(nombre_audio)
    except Exception as e:
        print("❌ Error al hablar:", e)

# 🎯 Intercepción de intención especial
def contar_clientes_activos(empresa_id):
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM clientes
            WHERE empresa_id = %s AND activo = TRUE
        """, (empresa_id,))
        total = cur.fetchone()[0]
        conn.close()
        return total
    except Exception as e:
        return f"[Error DB: {e}]"

# Función principal de respuesta
def responder_mate(empresa_id, mensaje):
    memoria = ConversationBufferMemory()
    historial = obtener_historial(empresa_id)

    for msg, resp in historial:
        memoria.chat_memory.add_user_message(msg)
        memoria.chat_memory.add_ai_message(resp)

    chatbot = ConversationChain(llm=llm, memory=memoria)

    # Intención simple
    if "clientes activos" in mensaje.lower():
        total = contar_clientes_activos(empresa_id)
        respuesta = f"Tienes {total} clientes activos registrados en el CRM."
    else:
        respuesta = chatbot.run(mensaje)

    guardar_interaccion(empresa_id, mensaje, respuesta)
    hablar(respuesta)

    return respuesta