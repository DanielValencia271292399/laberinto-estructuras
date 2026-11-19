# Laberinto: proyecto final de Estructuras de Datos

Juego de laberinto por turnos con interfaz gráfica. El jugador debe llegar desde la entrada hasta la salida **S** esquivando enemigos que patrullan el laberinto. Todas las estructuras de datos que usa el juego están **programadas desde cero con nodos y referencias**, sin `list`, `deque`, `queue` ni otras colecciones de Python.

| | |
|---|---|
| **Juego** | Laberinto |
| **Integrante** | Daniel Astudillo |
| **Lenguaje** | Python 3.10 o superior |
| **Interfaz** | Tkinter (viene incluida con Python) |
| **Librerías externas** | Ninguna |

## Cómo ejecutarlo

1. Instala Python 3.10 o superior desde <https://www.python.org/downloads/>. En Windows, marca la opción *"Add Python to PATH"*.
2. Descarga o clona el repositorio:
   ```bash
   git clone https://github.com/<tu-usuario>/laberinto-estructuras.git
   cd laberinto-estructuras
   ```
3. Ejecuta el juego:
   ```bash
   python main.py
   ```
   En Linux, si sale un error de Tkinter: `sudo apt install python3-tk`.

### Ejecutar las pruebas

```bash
python -m unittest -v
```

Son 47 pruebas automáticas: las estructuras, el laberinto, las reglas, los puntajes y una revisión del código que comprueba que las estructuras no usan colecciones de Python.

## Controles

| Tecla | Acción |
|---|---|
| Flechas o W A S D | Mover |
| Espacio | Esperar un turno |
| Z | Deshacer el último movimiento |
| H | Pista: camino más corto a la salida |
| Esc | Pausa / volver al menú |

## Estructuras de datos y su uso en el juego

| Estructura | Archivo | Uso en el juego |
|---|---|---|
| **Pila** | `estructuras/pila.py` | Generar el laberinto con *backtracking* y deshacer movimientos |
| **Cola** | `estructuras/cola.py` | BFS para la pista y el camino mínimo; enemigos en espera para entrar |
| **Lista circular** | `estructuras/lista_circular.py` | Ruta de patrulla de cada enemigo (ida y vuelta, se repite sin fin) |
| **Lista doble** | `estructuras/lista_doble.py` | Camino recorrido por el jugador y visor del recorrido adelante/atrás |
| **Árbol BST** | `estructuras/arbol_bst.py` | Tabla de mejores puntajes: ranking, búsqueda, eliminación y recorridos |

## Organización del código

```
laberinto-estructuras/
├── main.py                 # punto de entrada
├── estructuras/            # las 5 estructuras propias
│   ├── pila.py
│   ├── cola.py
│   ├── lista_circular.py
│   ├── lista_doble.py
│   └── arbol_bst.py
├── juego/                  # lógica del juego (sin interfaz)
│   ├── laberinto.py        # matriz, generación (pila) y BFS (cola)
│   ├── enemigo.py          # enemigos con ruta en lista circular
│   ├── partida.py          # reglas, turnos, vidas, deshacer, visor
│   └── puntajes.py         # tabla de puntajes con árbol BST
├── interfaz/
│   └── app.py              # interfaz gráfica con Tkinter
├── tests/                  # pruebas con unittest
└── docs/                   # manual de usuario y técnico (PDF)
```

## Documentación

El manual de usuario y el manual técnico están en [`docs/Manual_Laberinto.pdf`](docs/Manual_Laberinto.pdf).
