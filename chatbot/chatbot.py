import os
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# Cargar API Key desde .env
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

# Configurar salida de voz
voz = pyttsx3.init()
voz.setProperty('rate', 170)
voz.setProperty('volume', 1.0)

def hablar(texto):
    print(f"\n🤖 Mate: {texto}")
    voz.say(texto)
    voz.runAndWait()

# Configurar el modelo de IA con memoria
llm = ChatOpenAI(
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=api_key,
    model="openai/gpt-3.5-turbo",
    temperature=0.7
)

memoria = ConversationBufferMemory()
chatbot = ConversationChain(llm=llm, memory=memoria)

# Inicializar entrada por voz
reconocedor = sr.Recognizer()
microfono = sr.Microphone()

# Instrucciones iniciales
print("🤖 Mate activado: Hola, soy tu asistente. Puedes hablarme o escribirme.")
print("📌 Escribe 'texto' para escribir, 'voz' para hablar, o 'salir' para terminar.\n")

# Bucle principal
while True:
    modo = input("¿Modo [texto/voz]? ").strip().lower()

    if modo == "salir":
        hablar("Hasta pronto. ¡Seguimos en contacto!")
        break

    elif modo == "texto":
        entrada = input("Tú: ")
        if entrada.lower() in ['salir', 'terminar']:
            hablar("Hasta luego.")
            break
        respuesta = chatbot.run(entrada)
        hablar(respuesta)

    elif modo == "voz":
        print("🎧 Escuchando...")

        with microfono as source:
            reconocedor.adjust_for_ambient_noise(source)
            audio = reconocedor.listen(source)

        try:
            texto = reconocedor.recognize_google(audio, language="es-MX")
            print(f"🗣 Tú: {texto}")

            if texto.lower() in ['salir', 'terminar']:
                hablar("Hasta luego.")
                break

            respuesta = chatbot.run(texto)
            hablar(respuesta)

        except sr.UnknownValueError:
            print("❌ No entendí lo que dijiste.")
        except sr.RequestError:
            print("❌ Error al conectar con el servicio de voz.")

    else:
        print("❗ Escribe 'texto', 'voz' o 'salir'")
