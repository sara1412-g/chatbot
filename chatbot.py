""
chatbot.py
-----------
Chatbot domótico por voz para encender y apagar un LED conectado a una ESP32.

Flujo:
  Usuario habla -> Micrófono -> SpeechRecognition (texto)
      -> Intérprete de intención (reglas locales o API de IA)
      -> Comando ON / OFF
      -> Puerto serial USB -> ESP32 -> LED

Requisitos:
    pip install requests SpeechRecognition pyserial pyaudio

Uso:
    python chatbot.py
"""

import sys
import time
import serial
import requests
import speech_recognition as sr

# ------------------------------------------------------------------
# CONFIGURACIÓN
# ------------------------------------------------------------------
PUERTO_SERIAL = "COM5"      # Cambia esto por el puerto de tu ESP32
                             # En Linux/Mac suele ser algo como "/dev/ttyUSB0"
BAUDRATE = 115200

# Si quieres usar un modelo de IA (DeepSeek, OpenAI, etc.) para interpretar
# frases más naturales, coloca aquí tu API key. Si lo dejas vacío ("") el
# chatbot usará un intérprete de palabras clave 100% local (sin costo y
# sin necesidad de internet).
USAR_IA = False
DEEPSEEK_API_KEY = ""
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

IDIOMA_VOZ = "es-ES"


# ------------------------------------------------------------------
# 1. CAPTURA DE VOZ
# ------------------------------------------------------------------
def escuchar_microfono():
    """Captura audio del micrófono y lo convierte en texto."""
    reconocedor = sr.Recognizer()
    with sr.Microphone() as fuente:
        print("\n🎤 Escuchando... (di 'salir' para terminar)")
        reconocedor.adjust_for_ambient_noise(fuente, duration=0.5)
        audio = reconocedor.listen(fuente)

    try:
        texto = reconocedor.recognize_google(audio, language=IDIOMA_VOZ)
        print(f"Tú: {texto}")
        return texto.lower().strip()
    except sr.UnknownValueError:
        print("No entendí el audio, intenta de nuevo.")
        return ""
    except sr.RequestError as e:
        print(f"Error con el servicio de reconocimiento de voz: {e}")
        return ""


# ------------------------------------------------------------------
# 2. INTERPRETACIÓN DE LA INTENCIÓN
# ------------------------------------------------------------------
PALABRAS_ENCENDER = [
    "enciende", "encender", "prende", "prender", "activa", "activar",
    "ilumina", "iluminar", "on"
]
PALABRAS_APAGAR = [
    "apaga", "apagar", "apagalo", "desactiva", "desactivar",
    "quita la luz", "off", "ya no necesito"
]


def interpretar_local(texto):
    """Intérprete de intención basado en palabras clave (sin IA, sin internet)."""
    texto = texto.lower()
    if any(palabra in texto for palabra in PALABRAS_ENCENDER):
        return "ENCENDER"
    if any(palabra in texto for palabra in PALABRAS_APAGAR):
        return "APAGAR"
    return "DESCONOCIDO"


def interpretar_con_ia(texto):
    """Intérprete de intención usando la API de DeepSeek (opcional)."""
    if not DEEPSEEK_API_KEY:
        print("⚠️  No hay API key configurada, usando intérprete local.")
        return interpretar_local(texto)

    prompt_sistema = (
        "Eres un asistente domótico. El usuario te dará una frase en "
        "español relacionada con un LED o una luz. Debes responder "
        "ÚNICAMENTE con una de estas tres palabras, sin explicaciones: "
        "ENCENDER, APAGAR o DESCONOCIDO."
    )

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": texto},
        ],
        "max_tokens": 10,
        "temperature": 0,
    }

    try:
        respuesta = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=10)
        respuesta.raise_for_status()
        contenido = respuesta.json()["choices"][0]["message"]["content"].strip().upper()

        if "ENCENDER" in contenido:
            return "ENCENDER"
        if "APAGAR" in contenido:
            return "APAGAR"
        return "DESCONOCIDO"
    except Exception as e:
        print(f"⚠️  Error consultando la IA ({e}); usando intérprete local.")
        return interpretar_local(texto)


def interpretar_intencion(texto):
    if USAR_IA:
        return interpretar_con_ia(texto)
    return interpretar_local(texto)


# ------------------------------------------------------------------
# 3. COMUNICACIÓN SERIAL CON LA ESP32
# ------------------------------------------------------------------
def conectar_esp32(puerto, baudrate):
    try:
        conexion = serial.Serial(puerto, baudrate, timeout=2)
        time.sleep(2)  # esperar a que la ESP32 reinicie tras abrir el puerto
        print(f"✅ Conectado a la ESP32 en {puerto}")
        return conexion
    except serial.SerialException as e:
        print(f"❌ No se pudo abrir el puerto {puerto}: {e}")
        sys.exit(1)


def enviar_comando(conexion, comando):
    """Envía 'ON' u 'OFF' a la ESP32 por serial."""
    conexion.write(f"{comando}\n".encode("utf-8"))
    print(f"➡️  Comando enviado a la ESP32: {comando}")


# ------------------------------------------------------------------
# 4. PROGRAMA PRINCIPAL
# ------------------------------------------------------------------
def main():
    esp32 = conectar_esp32(PUERTO_SERIAL, BAUDRATE)

    print("=" * 50)
    print(" Chatbot Domótico - Control de LED por voz")
    print(" Ejemplos: 'enciende la luz', 'apaga el led'")
    print("=" * 50)

    while True:
        texto = escuchar_microfono()

        if not texto:
            continue

        if "salir" in texto or "adiós" in texto:
            print("👋 Cerrando chatbot...")
            break

        intencion = interpretar_intencion(texto)
        print(f"IA/Local: {intencion}")

        if intencion == "ENCENDER":
            enviar_comando(esp32, "ON")
        elif intencion == "APAGAR":
            enviar_comando(esp32, "OFF")
        else:
            print("🤔 No entendí si quieres encender o apagar el LED.")

    esp32.close()


if __name__ == "__main__":
    main()
