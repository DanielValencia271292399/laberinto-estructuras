"""
Punto de entrada del juego Laberinto.

Ejecutar desde la carpeta del proyecto:
    python main.py
"""

import os
import sys

# Asegura que los paquetes del proyecto se encuentren aunque se ejecute
# desde otra carpeta.
CARPETA = os.path.dirname(os.path.abspath(__file__))
if CARPETA not in sys.path:
    sys.path.insert(0, CARPETA)


def main():
    """Abre la ventana del juego. Si falta Tkinter, explica como instalarlo."""
    try:
        from interfaz.app import iniciar
    except ImportError as error:
        print("No se pudo cargar Tkinter:", error)
        print("En Windows/Mac viene con Python. En Linux: sudo apt install python3-tk")
        return
    iniciar(os.path.join(CARPETA, "puntajes.txt"))


if __name__ == "__main__":
    main()
