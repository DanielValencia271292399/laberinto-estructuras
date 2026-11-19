"""
Interfaz grafica del juego con Tkinter (incluida en Python).

Todo se dibuja sobre un solo Canvas. Hay varias "pantallas" (menu, nombre,
juego, fin, recorrido, puntajes, reglas); cada vez que algo cambia se
borra el canvas y se vuelve a dibujar la pantalla actual.

Los botones se guardan en una ListaDoble propia; al hacer clic se recorre
la lista para saber cual fue presionado.

La interfaz SOLO dibuja y recibe teclas/clics: las reglas estan en
juego/partida.py y las estructuras en estructuras/.
"""

import sys
import traceback
import tkinter as tk

from estructuras.lista_doble import ListaDoble
from juego.laberinto import Laberinto, PARED
from juego.partida import Partida, VisorRecorrido, DIFICULTADES, GANO, PERDIO, JUGANDO
from juego.puntajes import TablaPuntajes, Registro, validar_nombre, validar_puntaje

# ------------------------------------------------------------------ estilo
ANCHO, ALTO = 1000, 700
FUENTE = "Helvetica"
C_FONDO = "#0b1220"
C_PANEL = "#131c2e"
C_BORDE = "#2a3a5c"
C_TEXTO = "#e5e9f0"
C_SUAVE = "#94a3b8"
C_PARED = "#2b3a5a"
C_PISO = "#eef2f8"
C_JUGADOR = "#2563eb"
C_ENEMIGO = "#ef4444"
C_SALIDA = "#22c55e"
C_INICIO = "#c7d2fe"
C_RASTRO = "#93c5fd"
C_PISTA = "#f59e0b"
C_BOTON = "#1f2d4a"
C_BOTON_HOVER = "#2f4371"
C_ACENTO = "#38bdf8"
C_ERROR = "#f87171"
C_OK = "#4ade80"

NOMBRES_DIFICULTAD = {"Facil": "Fácil", "Medio": "Medio", "Dificil": "Difícil"}

# area donde se dibuja el tablero
TABLERO_X, TABLERO_Y, TABLERO_LADO = 24, 24, 652

# teclas de movimiento -> direccion
TECLAS_MOVER = {
    "Up": "arriba", "w": "arriba", "W": "arriba",
    "Down": "abajo", "s": "abajo", "S": "abajo",
    "Left": "izquierda", "a": "izquierda", "A": "izquierda",
    "Right": "derecha", "d": "derecha", "D": "derecha",
}


class Boton:
    """Rectangulo clicable dibujado en el canvas."""

    def __init__(self, x1, y1, x2, y2, texto, accion, activo=True, resaltado=False):
        """
        Recibe: coordenadas del rectangulo, texto, accion (funcion sin
        parametros), si esta activo y si se dibuja resaltado.
        """
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.texto = texto
        self.accion = accion
        self.activo = activo
        self.resaltado = resaltado

    def contiene(self, x, y):
        """Devuelve True si el punto (x, y) esta dentro del boton."""
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2


class AppLaberinto:
    """Ventana principal y control de pantallas."""

    def __init__(self, raiz, ruta_puntajes="puntajes.txt"):
        """
        Crea la ventana del juego.
        Recibe: raiz (tk.Tk) y la ruta del archivo de puntajes.
        Devuelve: nada.
        """
        self.raiz = raiz
        self.raiz.title("Laberinto - Estructuras de Datos")
        self.raiz.geometry(str(ANCHO) + "x" + str(ALTO))
        self.raiz.resizable(False, False)
        self.canvas = tk.Canvas(raiz, width=ANCHO, height=ALTO, bg=C_FONDO,
                                highlightthickness=0)
        self.canvas.pack()

        self.tabla = TablaPuntajes(ruta_puntajes)
        self.partida = None
        self.visor = None
        self.pantalla = "menu"
        self.botones = ListaDoble()
        self.hover = None
        self.indice_menu = 0

        # datos de los campos de texto
        self.texto_nombre = ""
        self.dificultad = "Facil"
        self.texto_buscar = ""
        self.aviso = ""          # mensaje de error/info en pantallas de texto
        self.aviso_error = False
        self.pausa = False
        self.resultado = None    # (puntaje, posicion) al terminar
        self.tipo_recorrido = "ranking"
        self.seleccion = None    # registro seleccionado en puntajes
        self.encontrado = None   # registro encontrado al buscar

        # laberinto decorativo para el menu
        self.lab_menu = Laberinto(9, 15, semilla=7, aberturas_extra=6)

        self.raiz.bind("<Key>", self._seguro(self.al_presionar_tecla))
        self.canvas.bind("<Button-1>", self._seguro(self.al_hacer_clic))
        self.canvas.bind("<Motion>", self._seguro(self.al_mover_mouse))
        self.raiz.protocol("WM_DELETE_WINDOW", self.raiz.destroy)
        self.dibujar()

    # ---------------------------------------------------------- utilidades
    def _seguro(self, funcion):
        """
        Envuelve un manejador de eventos para que un error inesperado NO
        cierre el juego: se muestra un aviso y se sigue jugando.
        Recibe: funcion(evento).  Devuelve: nueva funcion.
        """
        def envoltura(evento):
            try:
                funcion(evento)
            except Exception as error:  # noqa: BLE001 - el juego nunca se cierra
                traceback.print_exc(file=sys.stderr)
                self.aviso = "Error inesperado: " + str(error)
                self.aviso_error = True
                self.dibujar()
        return envoltura

    def ir_a(self, pantalla):
        """Cambia de pantalla y redibuja."""
        self.pantalla = pantalla
        self.aviso = ""
        self.aviso_error = False
        self.hover = None
        self.indice_menu = 0
        self.dibujar()

    def _avisar(self, texto, error=False):
        """Muestra un aviso en la pantalla actual."""
        self.aviso = texto
        self.aviso_error = error
        self.dibujar()

    # ------------------------------------------------------------- eventos
    def al_hacer_clic(self, evento):
        """Recorre la lista de botones y ejecuta el que fue presionado."""
        for boton in self.botones:
            if boton.activo and boton.contiene(evento.x, evento.y):
                boton.accion()
                return
        if self.pantalla == "puntajes":
            self._clic_en_tabla(evento.x, evento.y)

    def al_mover_mouse(self, evento):
        """Resalta el boton que esta bajo el mouse."""
        nuevo = None
        for boton in self.botones:
            if boton.activo and boton.contiene(evento.x, evento.y):
                nuevo = boton.texto
                break
        if nuevo != self.hover:
            self.hover = nuevo
            self.dibujar()

    def al_presionar_tecla(self, evento):
        """Envia la tecla al manejador de la pantalla actual."""
        tecla = evento.keysym
        caracter = evento.char
        manejador = {
            "menu": self._tecla_menu,
            "nombre": self._tecla_nombre,
            "juego": self._tecla_juego,
            "fin": self._tecla_fin,
            "recorrido": self._tecla_recorrido,
            "puntajes": self._tecla_puntajes,
            "reglas": self._tecla_reglas,
        }.get(self.pantalla)
        if manejador is not None:
            manejador(tecla, caracter)

    def _tecla_menu(self, tecla, caracter):
        """Flechas para elegir opcion del menu y Enter para aceptar."""
        if tecla in ("Up", "w", "W"):
            self.indice_menu = (self.indice_menu - 1) % 4
        elif tecla in ("Down", "s", "S"):
            self.indice_menu = (self.indice_menu + 1) % 4
        elif tecla in ("Return", "KP_Enter", "space"):
            opciones = ListaDoble()
            for boton in self.botones:
                opciones.insertar_final(boton)
            opciones.obtener(self.indice_menu).accion()
            return
        elif tecla == "Escape":
            self.raiz.destroy()
            return
        self.dibujar()

    def _tecla_nombre(self, tecla, caracter):
        """Escribe el nombre; valida cada caracter y el largo."""
        if tecla in ("Return", "KP_Enter"):
            self.comenzar_partida()
        elif tecla == "Escape":
            self.ir_a("menu")
        elif tecla == "BackSpace":
            self.texto_nombre = self.texto_nombre[:-1]
            self._avisar("")
        elif tecla == "Tab":
            claves = ("Facil", "Medio", "Dificil")
            self.dificultad = claves[(claves.index(self.dificultad) + 1) % 3]
            self.dibujar()
        elif caracter and caracter.isprintable():
            if len(self.texto_nombre) >= 12:
                self._avisar("Máximo 12 caracteres.", True)
            elif not (caracter.isalnum() or caracter in " -_"):
                self._avisar("Carácter no permitido: '" + caracter + "'", True)
            else:
                self.texto_nombre += caracter
                self._avisar("")

    def _tecla_juego(self, tecla, caracter):
        """Movimiento, esperar (Espacio), deshacer (Z), pista (H) y pausa (Esc)."""
        if self.pausa:
            if tecla in ("Escape", "Return", "n", "N"):
                self.pausa = False
            elif tecla in ("m", "M"):
                self.pausa = False
                self.ir_a("menu")
                return
            self.dibujar()
            return
        if tecla in TECLAS_MOVER:
            self.partida.mover(TECLAS_MOVER[tecla])
        elif tecla in ("z", "Z", "BackSpace"):
            self.partida.deshacer()
        elif tecla in ("h", "H"):
            self.partida.pedir_pista()
        elif tecla in ("space", "e", "E"):
            self.partida.esperar()
        elif tecla == "Escape":
            self.pausa = True
        elif caracter and caracter.isprintable():
            self.partida.mensaje = "Tecla no válida: '" + caracter + "'. Usa flechas/WASD, Espacio, Z o H."
        else:
            return  # teclas como Shift: no hacer nada
        self._revisar_fin()
        self.dibujar()

    def _tecla_fin(self, tecla, caracter):
        """Atajos en la pantalla de fin."""
        if tecla in ("r", "R"):
            self.abrir_recorrido()
        elif tecla in ("Return", "KP_Enter"):
            self.jugar_otra_vez()
        elif tecla == "Escape":
            self.ir_a("menu")

    def _tecla_recorrido(self, tecla, caracter):
        """Navega el camino (lista doble) con flechas, Inicio y Fin."""
        if tecla in ("Right", "d", "D"):
            self.visor.siguiente()
        elif tecla in ("Left", "a", "A"):
            self.visor.anterior()
        elif tecla in ("Home", "Up"):
            self.visor.ir_inicio()
        elif tecla in ("End", "Down"):
            self.visor.ir_final()
        elif tecla == "Escape":
            self.ir_a("fin")
            return
        self.dibujar()

    def _tecla_puntajes(self, tecla, caracter):
        """Campo para buscar un puntaje en el arbol."""
        if tecla in ("Return", "KP_Enter"):
            self.buscar_puntaje()
        elif tecla == "Escape":
            self.ir_a("menu")
        elif tecla == "BackSpace":
            self.texto_buscar = self.texto_buscar[:-1]
            self.dibujar()
        elif tecla == "Delete":
            self.eliminar_seleccion()
        elif caracter and caracter.isprintable():
            if len(self.texto_buscar) < 8:
                self.texto_buscar += caracter
            self.dibujar()

    def _tecla_reglas(self, tecla, caracter):
        """Cualquier Esc/Enter vuelve al menu."""
        if tecla in ("Escape", "Return", "KP_Enter"):
            self.ir_a("menu")

    # ---------------------------------------------------- acciones de juego
    def comenzar_partida(self):
        """Valida el nombre y crea una partida nueva."""
        valido, resultado = validar_nombre(self.texto_nombre)
        if not valido:
            self._avisar(resultado, True)
            return
        self.texto_nombre = resultado
        self.partida = Partida(resultado, self.dificultad)
        self.pausa = False
        self.resultado = None
        self.ir_a("juego")

    def jugar_otra_vez(self):
        """Nueva partida con el mismo nombre y dificultad."""
        self.comenzar_partida()

    def _revisar_fin(self):
        """Si la partida termino, guarda el puntaje y pasa a 'fin'."""
        if self.partida.estado == JUGANDO:
            return
        puntaje = self.partida.calcular_puntaje()
        posicion = None
        if self.partida.estado == GANO:
            registro = Registro(self.partida.nombre, puntaje,
                                NOMBRES_DIFICULTAD[self.partida.dificultad],
                                self.partida.pasos)
            posicion = self.tabla.agregar(registro)
        self.resultado = (puntaje, posicion)
        self.pantalla = "fin"
        self.hover = None

    def abrir_recorrido(self):
        """Crea el visor sobre la lista doble del camino."""
        self.visor = VisorRecorrido(self.partida.camino)
        self.ir_a("recorrido")

    def buscar_puntaje(self):
        """Busca en el arbol el puntaje escrito."""
        valido, valor = validar_puntaje(self.texto_buscar)
        if not valido:
            self.encontrado = None
            self._avisar(valor, True)
            return
        registro = self.tabla.buscar(valor)
        self.encontrado = registro
        if registro is None:
            self._avisar("No hay ningún registro con " + str(valor) + " puntos.", True)
        else:
            self.seleccion = registro
            self._avisar("Encontrado: " + str(registro), False)

    def eliminar_seleccion(self):
        """Elimina del arbol el registro seleccionado."""
        if self.seleccion is None:
            self._avisar("Primero selecciona un registro de la tabla.", True)
            return
        texto = str(self.seleccion)
        if self.tabla.eliminar(self.seleccion):
            self.seleccion = None
            self.encontrado = None
            self._avisar("Eliminado: " + texto, False)
        else:
            self._avisar("No se pudo eliminar.", True)

    def cambiar_recorrido(self, tipo):
        """Cambia el recorrido del arbol que se muestra en la tabla."""
        self.tipo_recorrido = tipo
        self.dibujar()

    def _clic_en_tabla(self, x, y):
        """Selecciona la fila de la tabla de puntajes donde se hizo clic."""
        if not (40 <= x <= 640):
            return
        fila = (y - 178) // 34
        registros = self._registros_tabla()
        if 0 <= fila < registros.tamano():
            self.seleccion = registros.obtener(fila)
            self._avisar("Seleccionado: " + str(self.seleccion) + "  (Supr o botón Eliminar)")

    def _registros_tabla(self):
        """Registros que se ven en la tabla segun el recorrido elegido."""
        if self.tipo_recorrido == "ranking":
            return self.tabla.ranking(12)
        todos = self.tabla.recorrido(self.tipo_recorrido)
        visibles = ListaDoble()
        for registro in todos:
            if visibles.tamano() >= 12:
                break
            visibles.insertar_final(registro)
        return visibles

    # ------------------------------------------------------------- dibujo
    def dibujar(self):
        """Borra el canvas y dibuja la pantalla actual."""
        self.canvas.delete("all")
        self.botones = ListaDoble()
        {
            "menu": self._dibujar_menu,
            "nombre": self._dibujar_nombre,
            "juego": self._dibujar_juego,
            "fin": self._dibujar_fin,
            "recorrido": self._dibujar_recorrido,
            "puntajes": self._dibujar_puntajes,
            "reglas": self._dibujar_reglas,
        }[self.pantalla]()

    def _boton(self, x1, y1, x2, y2, texto, accion, activo=True, resaltado=False, tam=14):
        """Dibuja un boton y lo agrega a la lista de botones."""
        boton = Boton(x1, y1, x2, y2, texto, accion, activo, resaltado)
        self.botones.insertar_final(boton)
        if not activo:
            relleno, borde, color = "#162036", "#23304b", "#55627a"
        elif resaltado or self.hover == texto:
            relleno, borde, color = C_BOTON_HOVER, C_ACENTO, "#ffffff"
        else:
            relleno, borde, color = C_BOTON, C_BORDE, C_TEXTO
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=relleno, outline=borde, width=2)
        self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=texto,
                                fill=color, font=(FUENTE, tam, "bold"))

    def _panel(self, x1, y1, x2, y2):
        """Rectangulo de fondo para agrupar informacion."""
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=C_PANEL, outline=C_BORDE, width=2)

    def _texto(self, x, y, texto, tam=13, color=C_TEXTO, peso="normal", anchor="nw", ancho=None):
        """Atajo para escribir texto."""
        opciones = {"text": texto, "fill": color, "font": (FUENTE, tam, peso), "anchor": anchor}
        if ancho is not None:
            opciones["width"] = ancho
        self.canvas.create_text(x, y, **opciones)

    def _dibujar_aviso(self, x, y, anchor="nw"):
        """Dibuja el aviso actual (rojo si es error)."""
        if self.aviso:
            self._texto(x, y, self.aviso, 13, C_ERROR if self.aviso_error else C_OK,
                        "bold", anchor)

    def _dibujar_laberinto(self, laberinto, x0, y0, lado, color_piso=C_PISO, color_pared=C_PARED):
        """
        Dibuja la matriz del laberinto dentro de un cuadrado.
        Devuelve: (tam, ox, oy) = tamano de casilla y origen, para ubicar
        al jugador, enemigos, etc.
        """
        tam = lado // max(laberinto.alto, laberinto.ancho)
        ox = x0 + (lado - tam * laberinto.ancho) // 2
        oy = y0 + (lado - tam * laberinto.alto) // 2
        self.canvas.create_rectangle(ox, oy, ox + tam * laberinto.ancho,
                                     oy + tam * laberinto.alto, fill=color_piso, outline="")
        for f in range(laberinto.alto):
            c = 0
            while c < laberinto.ancho:
                if laberinto.matriz[f][c] == PARED:
                    inicio = c  # juntar paredes seguidas en un solo rectangulo
                    while c < laberinto.ancho and laberinto.matriz[f][c] == PARED:
                        c += 1
                    self.canvas.create_rectangle(ox + inicio * tam, oy + f * tam,
                                                 ox + c * tam, oy + (f + 1) * tam,
                                                 fill=color_pared, outline="")
                else:
                    c += 1
        return tam, ox, oy

    def _casilla(self, posicion, tam, ox, oy, color, margen=0.0, ovalo=False, borde=""):
        """Pinta una casilla (rectangulo u ovalo) del tablero."""
        f, c = posicion
        m = tam * margen
        x1, y1 = ox + c * tam + m, oy + f * tam + m
        x2, y2 = ox + (c + 1) * tam - m, oy + (f + 1) * tam - m
        if ovalo:
            self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline=borde)
        else:
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=borde)

    def _dibujar_enemigo(self, posicion, tam, ox, oy):
        """Enemigo: circulo rojo con dos ojos."""
        self._casilla(posicion, tam, ox, oy, C_ENEMIGO, 0.08, True, "#7f1d1d")
        f, c = posicion
        cx, cy = ox + c * tam + tam / 2, oy + f * tam + tam / 2
        r = tam * 0.12
        for dx in (-tam * 0.17, tam * 0.17):
            self.canvas.create_oval(cx + dx - r, cy - r * 1.6, cx + dx + r, cy + r * 0.4,
                                    fill="white", outline="")

    def _dibujar_jugador(self, posicion, tam, ox, oy):
        """Jugador: circulo azul con borde blanco."""
        self._casilla(posicion, tam, ox, oy, C_JUGADOR, 0.1, True, "#ffffff")

    def _dibujar_salida(self, laberinto, tam, ox, oy):
        """Marca inicio y salida."""
        self._casilla(laberinto.inicio, tam, ox, oy, C_INICIO)
        self._casilla(laberinto.salida, tam, ox, oy, C_SALIDA)
        f, c = laberinto.salida
        self.canvas.create_text(ox + c * tam + tam / 2, oy + f * tam + tam / 2, text="S",
                                fill="white", font=(FUENTE, max(7, int(tam * 0.45)), "bold"))

    # --- menu
    def _dibujar_menu(self):
        """Pantalla de inicio con laberinto decorativo de fondo."""
        self._dibujar_laberinto(self.lab_menu, 0, -150, ANCHO, "#121b2d", "#0d1525")
        self.canvas.create_rectangle(300, 90, 700, 640, fill=C_PANEL, outline=C_BORDE, width=2)
        self._texto(500, 150, "LABERINTO", 40, C_ACENTO, "bold", "center")
        self._texto(500, 200, "Escapa, esquiva y llega a la salida", 14, C_SUAVE, "normal", "center")
        opciones = (("Jugar", lambda: self.ir_a("nombre")),
                    ("Reglas", lambda: self.ir_a("reglas")),
                    ("Puntajes", lambda: self.ir_a("puntajes")),
                    ("Salir", self.raiz.destroy))
        for i, (texto, accion) in enumerate(opciones):
            y = 260 + i * 72
            self._boton(380, y, 620, y + 52, texto, accion,
                        resaltado=(i == self.indice_menu), tam=17)
        self._texto(500, 575, "Flechas + Enter o clic", 12, C_SUAVE, "normal", "center")
        self._texto(500, 605, "Proyecto final · Estructuras de Datos · Daniel Astudillo",
                    11, C_SUAVE, "normal", "center")

    # --- nombre y dificultad
    def _dibujar_nombre(self):
        """Formulario para el nombre del jugador y la dificultad."""
        self._panel(220, 90, 780, 610)
        self._texto(500, 135, "Nueva partida", 26, C_TEXTO, "bold", "center")
        self._texto(270, 190, "Nombre del jugador (1 a 12 letras o números):", 13, C_SUAVE)
        self.canvas.create_rectangle(270, 220, 730, 270, fill="#0b1220", outline=C_ACENTO, width=2)
        self._texto(285, 245, self.texto_nombre + "|", 18, C_TEXTO, "bold", "w")
        self._dibujar_aviso(270, 282)

        self._texto(270, 330, "Dificultad (clic o Tab):", 13, C_SUAVE)
        x = 270
        for clave in ("Facil", "Medio", "Dificil"):
            self._boton(x, 360, x + 140, 410, NOMBRES_DIFICULTAD[clave],
                        lambda c=clave: self._elegir_dificultad(c),
                        resaltado=(clave == self.dificultad), tam=15)
            x += 160
        cfg = DIFICULTADES[self.dificultad]
        detalle = (str(cfg["filas"]) + "x" + str(cfg["columnas"]) + " celdas  ·  "
                   + str(cfg["enemigos"]) + " enemigos  ·  sale uno cada "
                   + str(cfg["intervalo"]) + " turnos  ·  " + str(cfg["pistas"]) + " pistas")
        self._texto(500, 432, detalle, 12, C_SUAVE, "normal", "center")
        self._boton(270, 490, 490, 545, "Comenzar", self.comenzar_partida, tam=16)
        self._boton(510, 490, 730, 545, "Volver", lambda: self.ir_a("menu"), tam=16)
        self._texto(500, 575, "Enter = comenzar  ·  Esc = volver", 11, C_SUAVE, "normal", "center")

    def _elegir_dificultad(self, clave):
        """Cambia la dificultad elegida."""
        self.dificultad = clave
        self.dibujar()

    # --- juego
    def _dibujar_tablero_partida(self):
        """Dibuja laberinto, rastro, pista, enemigos y jugador."""
        p = self.partida
        tam, ox, oy = self._dibujar_laberinto(p.laberinto, TABLERO_X, TABLERO_Y, TABLERO_LADO)
        self._dibujar_salida(p.laberinto, tam, ox, oy)
        for posicion in p.camino:  # rastro (lista doble)
            self._casilla(posicion, tam, ox, oy, C_RASTRO, 0.34, True)
        if p.pista is not None:   # pista (camino BFS)
            for posicion in p.pista:
                self._casilla(posicion, tam, ox, oy, C_PISTA, 0.3, True)
        for enemigo in p.enemigos_activos:
            self._dibujar_enemigo(enemigo.posicion, tam, ox, oy)
        self._dibujar_jugador(p.jugador, tam, ox, oy)
        return tam, ox, oy

    def _dibujar_juego(self):
        """Pantalla principal de juego: tablero + panel lateral."""
        p = self.partida
        self._dibujar_tablero_partida()

        x = 700
        self._panel(x, 24, 976, 676)
        self._texto(x + 18, 40, p.nombre, 20, C_ACENTO, "bold")
        self._texto(x + 18, 72, "Dificultad: " + NOMBRES_DIFICULTAD[p.dificultad], 13, C_SUAVE)

        self._texto(x + 18, 108, "Vidas", 12, C_SUAVE)
        for i in range(3):
            color = C_ENEMIGO if i < p.vidas else "#33415c"
            self.canvas.create_oval(x + 18 + i * 30, 130, x + 42 + i * 30, 154, fill=color, outline="")

        filas = (("Pasos", str(p.pasos) + " / " + str(p.limite_pasos)),
                 ("Pasos mínimos (BFS)", str(p.pasos_optimos)),
                 ("Pistas", str(p.pistas_restantes)),
                 ("Deshacer usados", str(p.deshacer_usados)),
                 ("Pila deshacer", str(p.pila_deshacer.tamano())),
                 ("Enemigos activos", str(p.enemigos_activos.tamano())),
                 ("Enemigos en espera", str(p.enemigos_espera.tamano())),
                 ("Camino (lista doble)", str(p.camino.tamano())))
        y = 172
        for etiqueta, valor in filas:
            self._texto(x + 18, y, etiqueta, 12, C_SUAVE)
            self._texto(x + 258, y, valor, 12, C_TEXTO, "bold", "ne")
            y += 25

        # barra de pasos restantes
        usado = min(1.0, p.pasos / float(p.limite_pasos))
        self.canvas.create_rectangle(x + 18, y + 4, x + 258, y + 14, fill="#22304d", outline="")
        color = C_OK if usado < 0.6 else (C_PISTA if usado < 0.85 else C_ENEMIGO)
        self.canvas.create_rectangle(x + 18, y + 4, x + 18 + 240 * (1 - usado), y + 14,
                                     fill=color, outline="")

        self._boton(x + 18, 400, x + 134, 440, "Pista (H)", self._accion_pista,
                    activo=p.pistas_restantes > 0, tam=12)
        self._boton(x + 142, 400, x + 258, 440, "Deshacer (Z)", self._accion_deshacer,
                    activo=not p.pila_deshacer.esta_vacia(), tam=12)
        self._boton(x + 18, 448, x + 258, 484, "Pausa / Menú (Esc)", self._accion_pausa, tam=12)

        self._texto(x + 18, 500, "Controles", 12, C_SUAVE, "bold")
        self._texto(x + 18, 520, "Flechas o WASD: mover\nEspacio: esperar un turno\nZ: deshacer   H: pista   Esc: pausa",
                    11, C_TEXTO)
        self.canvas.create_rectangle(x + 18, 584, x + 258, 660, fill="#0b1220", outline=C_BORDE)
        self._texto(x + 28, 592, p.mensaje, 12, C_PISTA if p.mensaje else C_SUAVE, "bold",
                    ancho=220)

        if self.pausa:
            self.canvas.create_rectangle(TABLERO_X, 250, TABLERO_X + TABLERO_LADO, 450,
                                         fill=C_PANEL, outline=C_ACENTO, width=3)
            self._texto(350, 290, "Pausa", 26, C_TEXTO, "bold", "center")
            self._boton(130, 340, 330, 395, "Seguir", self._accion_pausa, tam=15)
            self._boton(370, 340, 570, 395, "Salir al menú", lambda: self.ir_a("menu"), tam=15)
            self._texto(350, 420, "Esc = seguir  ·  M = menú (se pierde la partida)", 11,
                        C_SUAVE, "normal", "center")

    def _accion_pista(self):
        """Boton de pista."""
        self.partida.pedir_pista()
        self.dibujar()

    def _accion_deshacer(self):
        """Boton de deshacer."""
        self.partida.deshacer()
        self._revisar_fin()
        self.dibujar()

    def _accion_pausa(self):
        """Activa o quita la pausa."""
        self.pausa = not self.pausa
        self.dibujar()

    # --- fin
    def _dibujar_fin(self):
        """Resultado de la partida sobre el tablero final."""
        p = self.partida
        self._dibujar_tablero_partida()
        self._panel(250, 120, 750, 590)
        gano = p.estado == GANO
        self._texto(500, 175, "¡GANASTE!" if gano else "PERDISTE", 36,
                    C_OK if gano else C_ERROR, "bold", "center")
        self._texto(500, 225, p.mensaje, 14, C_SUAVE, "normal", "center")
        puntaje, posicion = self.resultado
        lineas = (("Jugador", p.nombre),
                  ("Dificultad", NOMBRES_DIFICULTAD[p.dificultad]),
                  ("Pasos / mínimos", str(p.pasos) + " / " + str(p.pasos_optimos)),
                  ("Vidas restantes", str(max(0, p.vidas))),
                  ("Deshacer · Pistas", str(p.deshacer_usados) + " · " + str(p.pistas_usadas)),
                  ("Puntaje", str(puntaje)))
        y = 262
        for etiqueta, valor in lineas:
            self._texto(320, y, etiqueta, 14, C_SUAVE)
            self._texto(680, y, valor, 14, C_TEXTO, "bold", "ne")
            y += 32
        if gano and posicion is not None:
            self._texto(500, y + 8, "Quedaste en el puesto #" + str(posicion) + " del ranking",
                        14, C_ACENTO, "bold", "center")
        self._boton(280, 500, 420, 550, "Ver recorrido", self.abrir_recorrido, tam=13)
        self._boton(430, 500, 570, 550, "Jugar otra vez", self.jugar_otra_vez, tam=13)
        self._boton(580, 500, 720, 550, "Menú", lambda: self.ir_a("menu"), tam=13)
        self._texto(500, 568, "R = recorrido · Enter = otra vez · Esc = menú", 11, C_SUAVE,
                    "normal", "center")

    # --- recorrido
    def _dibujar_recorrido(self):
        """Visor paso a paso del camino (lista doble)."""
        p = self.partida
        tam, ox, oy = self._dibujar_laberinto(p.laberinto, TABLERO_X, TABLERO_Y, TABLERO_LADO)
        self._dibujar_salida(p.laberinto, tam, ox, oy)
        # pasos ya recorridos hasta el visor (se recorre la lista doble)
        nodo = p.camino.cabeza
        i = 0
        while nodo is not None and i <= self.visor.indice:
            self._casilla(nodo.dato, tam, ox, oy, C_RASTRO, 0.3, True)
            nodo = nodo.siguiente
            i += 1
        self._dibujar_jugador(self.visor.actual(), tam, ox, oy)

        x = 700
        self._panel(x, 24, 976, 676)
        self._texto(x + 18, 40, "Recorrido", 22, C_ACENTO, "bold")
        self._texto(x + 18, 76, "Camino guardado en una lista\ndoblemente enlazada.", 12, C_SUAVE)
        total = p.camino.tamano()
        self._texto(x + 18, 130, "Paso " + str(self.visor.indice) + " de " + str(total - 1),
                    18, C_TEXTO, "bold")
        self._texto(x + 18, 162, "Casilla " + str(self.visor.actual()), 13, C_SUAVE)
        nodo = self.visor.nodo
        self._texto(x + 18, 192, "Anterior: " + (str(nodo.anterior.dato) if nodo.anterior else "—"),
                    12, C_SUAVE)
        self._texto(x + 18, 214, "Siguiente: " + (str(nodo.siguiente.dato) if nodo.siguiente else "—"),
                    12, C_SUAVE)
        self._boton(x + 18, 260, x + 72, 305, "|<<", self._visor_inicio, tam=14)
        self._boton(x + 80, 260, x + 134, 305, "<", self._visor_atras, tam=14)
        self._boton(x + 142, 260, x + 196, 305, ">", self._visor_adelante, tam=14)
        self._boton(x + 204, 260, x + 258, 305, ">>|", self._visor_final, tam=14)
        self._texto(x + 18, 325, "← → : paso a paso\nInicio/Fin: extremos\nEsc: volver",
                    12, C_TEXTO)
        self._boton(x + 18, 600, x + 258, 650, "Volver", lambda: self.ir_a("fin"), tam=14)

    def _visor_inicio(self):
        self.visor.ir_inicio()
        self.dibujar()

    def _visor_atras(self):
        self.visor.anterior()
        self.dibujar()

    def _visor_adelante(self):
        self.visor.siguiente()
        self.dibujar()

    def _visor_final(self):
        self.visor.ir_final()
        self.dibujar()

    # --- puntajes
    def _dibujar_puntajes(self):
        """Tabla de puntajes (arbol BST) con recorridos, busqueda y borrado."""
        self._texto(40, 30, "Mejores puntajes", 26, C_TEXTO, "bold")
        arbol = self.tabla.arbol
        self._texto(40, 72, "Árbol BST · nodos: " + str(arbol.tamano()) + " · altura: "
                    + str(arbol.altura()), 13, C_SUAVE)
        x = 40
        for tipo, texto in (("ranking", "Ranking"), ("inorden", "Inorden"),
                            ("preorden", "Preorden"), ("posorden", "Posorden")):
            self._boton(x, 100, x + 138, 138, texto, lambda t=tipo: self.cambiar_recorrido(t),
                        resaltado=(self.tipo_recorrido == tipo), tam=13)
            x += 150

        self._panel(40, 148, 640, 600)
        encabezados = ((60, "#"), (110, "Jugador"), (290, "Puntaje"), (390, "Dificultad"), (500, "Fecha"))
        for cx, texto in encabezados:
            self._texto(cx, 156, texto, 12, C_SUAVE, "bold")
        registros = self._registros_tabla()
        if registros.esta_vacia():
            self._texto(340, 360, "Aún no hay puntajes. ¡Gana una partida!", 15, C_SUAVE,
                        "normal", "center")
        y = 178
        for i, r in enumerate(registros):
            if r is self.seleccion:
                self.canvas.create_rectangle(44, y, 636, y + 32, fill="#1e3a5f", outline=C_ACENTO)
            valores = (str(i + 1), r.nombre, str(r.puntaje), r.dificultad, r.fecha)
            for (cx, _), valor in zip(encabezados, valores):
                self._texto(cx, y + 8, valor, 13, C_TEXTO)
            y += 34

        x = 670
        self._panel(x, 148, 960, 600)
        self._texto(x + 18, 164, "Buscar puntaje exacto", 14, C_TEXTO, "bold")
        self.canvas.create_rectangle(x + 18, 196, x + 272, 238, fill="#0b1220", outline=C_ACENTO, width=2)
        self._texto(x + 30, 217, self.texto_buscar + "|", 16, C_TEXTO, "bold", "w")
        self._boton(x + 18, 248, x + 272, 288, "Buscar (Enter)", self.buscar_puntaje, tam=13)
        if self.encontrado is not None:
            r = self.encontrado
            self._texto(x + 18, 300, r.nombre + "\n" + str(r.puntaje) + " pts · " + r.dificultad
                        + "\n" + str(r.pasos) + " pasos · " + r.fecha, 12, C_OK)
        self._texto(x + 18, 380, "Clic en una fila para\nseleccionarla.", 12, C_SUAVE)
        self._boton(x + 18, 430, x + 272, 470, "Eliminar seleccionado", self.eliminar_seleccion,
                    activo=self.seleccion is not None, tam=13)
        self._texto(x + 18, 490, "Ranking = inorden inverso\n(de mayor a menor).", 11, C_SUAVE)
        self._dibujar_aviso(40, 615)
        self._boton(760, 625, 960, 670, "Volver", lambda: self.ir_a("menu"), tam=14)

    # --- reglas
    def _dibujar_reglas(self):
        """Reglas y controles del juego."""
        self._panel(60, 30, 940, 670)
        self._texto(500, 70, "Reglas del juego", 26, C_ACENTO, "bold", "center")
        reglas = (
            "Objetivo: lleva tu ficha azul desde el inicio (arriba a la izquierda) hasta la "
            "salida verde S (abajo a la derecha).",
            "El juego es por turnos: cada vez que te mueves, esperas (Espacio) o deshaces, "
            "todos los enemigos avanzan un paso por su ruta de patrulla.",
            "Los enemigos (rojos) esperan en una cola y entran al laberinto uno por uno cada "
            "cierto número de turnos.",
            "Si un enemigo te toca pierdes una vida y vuelves al inicio. Tienes 3 vidas.",
            "Pierdes si te quedas sin vidas o si gastas todos los pasos permitidos.",
            "Deshacer (Z) te regresa a la casilla anterior, pero cuenta como turno y resta puntos.",
            "Pista (H) muestra el camino más corto a la salida durante unos turnos. Son limitadas.",
            "Puntaje = base de dificultad + 200 por vida − 5 por paso de más sobre el mínimo "
            "− 10 por deshacer − 100 por pista.",
            "Al terminar puedes ver tu recorrido paso a paso, hacia adelante y hacia atrás.",
        )
        y = 115
        for regla in reglas:
            self.canvas.create_oval(95, y + 6, 105, y + 16, fill=C_ACENTO, outline="")
            self._texto(120, y, regla, 13, C_TEXTO, ancho=780)
            y += 52
        self._boton(400, 600, 600, 645, "Volver", lambda: self.ir_a("menu"), tam=14)


def iniciar(ruta_puntajes="puntajes.txt"):
    """Crea la ventana y arranca el ciclo de eventos de Tkinter."""
    raiz = tk.Tk()
    AppLaberinto(raiz, ruta_puntajes)
    raiz.mainloop()
