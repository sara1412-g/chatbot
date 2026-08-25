"""
main.py
--------
Firmware MicroPython para la ESP32.

Escucha comandos por el puerto serial (USB) y enciende/apaga un LED
conectado al GPIO indicado.

Comandos aceptados (uno por línea):
    ON   -> enciende el LED
    OFF  -> apaga el LED

Cargar en la ESP32 con mpremote, por ejemplo:
    python -m mpremote connect COM5 fs cp main.py :main.py
    python -m mpremote connect COM5 reset
"""

from machine import Pin
import sys

# ------------------------------------------------------------------
# CONFIGURACIÓN DE HARDWARE
# ------------------------------------------------------------------
PIN_LED = 2          # GPIO donde está conectado el LED (ajusta según tu montaje)
led = Pin(PIN_LED, Pin.OUT)
led.value(0)         # Estado inicial: apagado


def encender():
    led.value(1)
    print("LED encendido")


def apagar():
    led.value(0)
    print("LED apagado")


def procesar_comando(comando):
    comando = comando.strip().upper()
    if comando == "ON":
        encender()
    elif comando == "OFF":
        apagar()
    elif comando:
        print("Comando no reconocido:", comando)


def main():
    print("ESP32 lista. Esperando comandos ON / OFF por serial...")
    while True:
        try:
            linea = sys.stdin.readline()
            if linea:
                procesar_comando(linea)
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
