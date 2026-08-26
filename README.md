[README (2).md](https://github.com/user-attachments/files/31429443/README.2.md)
#  Chatbot Domótico para Control de un LED por Voz

## Descripción

Este proyecto consiste en un **chatbot domótico capaz de encender y apagar un LED mediante comandos de voz**.

El sistema utiliza **Python** para capturar y reconocer la voz del usuario, interpreta la intención del comando (de forma local por palabras clave, o de forma opcional con una API de IA tipo DeepSeek) y envía la instrucción mediante **comunicación serial** a una **ESP32**, que controla físicamente el LED.

Ejemplos de frases que el chatbot entiende:

- **"Enciende la luz"**
- **"Prende el led"**
- **"Apaga la luz"**
- **"Ya no necesito la iluminación"**

## Objetivo

Desarrollar un sistema domótico básico que integre **reconocimiento de voz, interpretación de intención y una ESP32** para controlar el encendido y apagado de un LED mediante órdenes habladas.

## Componentes utilizados

### Hardware
- ESP32
- 1 LED
- 1 resistencia de aproximadamente 1 kΩ
- Protoboard
- Cables de conexión
- Cable USB
- Computador con micrófono

### Software
- Python 3
- Visual Studio Code
- MicroPython
- Wokwi para simulación

### Librerías de Python

```
pip install requests SpeechRecognition pyserial pyaudio
```

También se utiliza `mpremote` para cargar y administrar los archivos en la ESP32:

```
pip install mpremote
```

## Funcionamiento del sistema

```
Usuario
   │
   ▼
Comando de voz
   │
   ▼
Micrófono del computador
   │
   ▼
SpeechRecognition (voz -> texto)
   │
   ▼
Intérprete de intención (local o IA)
   │
   ├── ENCENDER
   │
   └── APAGAR
   │
   ▼
Python (chatbot.py)
   │
   ▼
Comunicación Serial USB
   │
   ▼
ESP32 (main.py)
   │
   └── GPIO 2 -> LED
```

1. `chatbot.py` escucha al usuario y convierte su voz en texto con `SpeechRecognition`.
2. El texto se analiza para detectar la intención (`ENCENDER`, `APAGAR` o `DESCONOCIDO`), usando un intérprete local por palabras clave o, si se activa, la API de una IA.
3. Si la intención es `ENCENDER`, se envía `ON` por el puerto serial. Si es `APAGAR`, se envía `OFF`.
4. La ESP32 (`main.py`, en MicroPython) recibe el comando por serial y actualiza el estado del GPIO conectado al LED.

## Conexión del LED

| Componente | Pin ESP32 |
| ---------- | --------- |
| LED        | GPIO 2    |
| Tierra     | GND       |

```
GPIO 2 ── Resistencia ── LED ── GND
```

## Archivos del proyecto

```
chatbot_led_domotico/
│
├── chatbot.py       # Programa que corre en el computador
├── main.py           # Programa que corre en la ESP32 (MicroPython)
├── diagram.json       # Circuito de simulación en Wokwi
└── README.md          # Este archivo
```

### `chatbot.py`
Corre en el computador. Se encarga de:
- Capturar la voz mediante el micrófono.
- Convertir la voz en texto.
- Interpretar el texto (local o con IA) para saber si el usuario quiere encender o apagar el LED.
- Comunicarse con la ESP32 mediante el puerto serial.

### `main.py`
Se carga en la ESP32 con MicroPython. Se encarga de:
- Esperar comandos por comunicación serial.
- Recibir `ON` u `OFF`.
- Encender o apagar el LED en el GPIO configurado.

### `diagram.json`
Contiene la configuración del circuito para simular el proyecto en Wokwi.

## Ejecución

1. Cargar `main.py` en la ESP32.

   Verificar el puerto disponible:

   ```
   python -m serial.tools.list_ports
   ```

   Cargar el archivo (ejemplo con el puerto `COM5`):

   ```
   python -m mpremote connect COM5 fs cp main.py :main.py
   ```

   Comprobar que el archivo quedó en la ESP32:

   ```
   python -m mpremote connect COM5 fs ls
   ```

   Reiniciar la placa:

   ```
   python -m mpremote connect COM5 reset
   ```

2. Ejecutar el chatbot desde el computador:

   ```
   python chatbot.py
   ```

> Antes de ejecutar, edita `PUERTO_SERIAL` en `chatbot.py` con el puerto correcto de tu ESP32 (por ejemplo `COM5` en Windows o `/dev/ttyUSB0` en Linux/Mac).

## Ejemplo de funcionamiento

El usuario dice:

```
"Enciende la luz"
```

El reconocimiento de voz obtiene:

```
Tú: enciende la luz
```

El intérprete determina la intención:

```
IA/Local: ENCENDER
```

Python envía a la ESP32:

```
ON
```

La ESP32 enciende el LED.

De forma similar, si el usuario dice `"Apaga la luz"`, el sistema envía `OFF` y la ESP32 apaga el LED.

## Uso opcional de una API de IA

Por defecto, `chatbot.py` interpreta la voz usando un diccionario de palabras clave (sin costo, sin internet). Si prefieres que la interpretación sea más flexible con frases naturales, puedes activar el uso de una API de IA (como DeepSeek):

1. En `chatbot.py`, cambia `USAR_IA = True`.
2. Coloca tu API key en `DEEPSEEK_API_KEY`.

## video 
<video src="https://github.com/user-attachments/assets/REEMPLAZAR-videochatbot-" controls width="500"></video>

📹 Archivo: [`evidencias/videos/deteccion_videochatbot.mp4`](./evidencias/videos/deteccion_videochatbot.mp4)

## Conclusión

Este proyecto permite aplicar conceptos básicos de **domótica, programación en Python, MicroPython y comunicación serial**, integrando reconocimiento de voz para controlar un dispositivo físico. Aunque aquí se controla un solo LED, el mismo principio puede ampliarse para controlar más LEDs, lámparas, ventiladores, motores, relés u otros elementos de una vivienda inteligente.
