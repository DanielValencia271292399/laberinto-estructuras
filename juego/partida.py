"""
Estado y reglas de una partida del Laberinto (sin interfaz grafica).

Aqui se juntan las 5 estructuras:
  - PILA       : deshacer movimientos (posiciones anteriores del jugador).
                 (Laberinto tambien usa una pila para generarse.)
  - COLA       : enemigos en espera que van saliendo por turnos.
                 (Laberinto usa otra cola para el BFS de la pista.)
  - L. CIRCULAR: ruta de patrulla de cada enemigo.
  - L. DOBLE   : camino recorrido por el jugador y visor del recorrido.
  - ARBOL BST  : puntajes (ver puntajes.py).

El juego es POR TURNOS: cada accion del jugador (mover, esperar o
deshacer) es un turno, y en cada turno los enemigos avanzan un paso.
"""

import random

from estructuras.pila import Pila
from estructuras.cola import Cola
from estructuras.lista_doble import ListaDoble
from juego.laberinto import Laberinto, DIRECCIONES
from juego.enemigo import Enemigo, construir_ruta_ida_vuelta

JUGANDO = "jugando"
GANO = "gano"
PERDIO = "perdio"

# Configuracion de cada dificultad
DIFICULTADES = {
    "Facil": {"filas": 9, "columnas": 9, "enemigos": 2, "intervalo": 8,
              "aberturas": 10, "pistas": 3, "factor_pasos": 4, "base": 1000},
    "Medio": {"filas": 13, "columnas": 13, "enemigos": 4, "intervalo": 6,
              "aberturas": 20, "pistas": 2, "factor_pasos": 3, "base": 2000},
    "Dificil": {"filas": 17, "columnas": 17, "enemigos": 6, "intervalo": 4,
                "aberturas": 30, "pistas": 1, "factor_pasos": 3, "base": 3000},
}
VIDAS_INICIALES = 3
TURNOS_PISTA = 6          # turnos que se ve la pista en pantalla
DISTANCIA_SEGURA = 4      # los enemigos no patrullan tan cerca del inicio


class Partida:
    """Una partida completa: laberinto, jugador, enemigos y reglas."""

    def __init__(self, nombre, dificultad="Facil", semilla=None):
        """
        Prepara una partida nueva.
        Recibe:
          nombre: nombre del jugador (ya validado).
          dificultad: "Facil", "Medio" o "Dificil".
          semilla: numero para repetir la misma partida (pruebas).
        Devuelve: nada.
        Lanza: ValueError si la dificultad no existe.
        """
        if dificultad not in DIFICULTADES:
            raise ValueError("dificultad no valida: " + str(dificultad))
        self.nombre = nombre
        self.dificultad = dificultad
        self.config = DIFICULTADES[dificultad]
        self.azar = random.Random(semilla)
        self.laberinto = Laberinto(self.config["filas"], self.config["columnas"],
                                   semilla=self.azar.randrange(10 ** 9),
                                   aberturas_extra=self.config["aberturas"])
        self.jugador = self.laberinto.inicio
        self.estado = JUGANDO
        self.vidas = VIDAS_INICIALES
        self.turno = 0
        self.pasos = 0
        self.deshacer_usados = 0
        self.pistas_restantes = self.config["pistas"]
        self.pistas_usadas = 0
        self.golpes = 0
        self.mensaje = "Llega a la salida verde. Cuidado con los enemigos."

        # PILA: posiciones anteriores para deshacer
        self.pila_deshacer = Pila()
        # LISTA DOBLE: todo el camino recorrido (incluye el inicio)
        self.camino = ListaDoble()
        self.camino.insertar_final(self.jugador)
        # Pista visible (camino del BFS) y cuantos turnos le quedan
        self.pista = None
        self.turnos_pista = 0

        # Pasos minimos para ganar (BFS) y limite de pasos de la partida
        self.pasos_optimos = self.laberinto.distancia(self.laberinto.inicio,
                                                      self.laberinto.salida)
        self.limite_pasos = self.pasos_optimos * self.config["factor_pasos"] + 20

        # COLA: enemigos esperando a entrar; LISTA DOBLE: enemigos activos
        self.enemigos_espera = Cola()
        self.enemigos_activos = ListaDoble()
        self._crear_enemigos()

    # --------------------------------------------------------------- enemigos
    def _crear_enemigos(self):
        """
        Crea los enemigos con rutas al azar y los encola en espera.
        Cada ruta es el camino mas corto (BFS) entre dos casillas al azar,
        convertido a ruta circular de ida y vuelta.
        """
        pisos = self.laberinto.celdas_de_piso()
        for numero in range(1, self.config["enemigos"] + 1):
            ruta = self._ruta_aleatoria(pisos)
            self.enemigos_espera.encolar(Enemigo("Enemigo " + str(numero), ruta))

    def _ruta_aleatoria(self, pisos):
        """
        Busca una ruta de patrulla lejos del inicio y de la salida, y que
        no tape el unico camino hacia la salida.
        Recibe: pisos (ListaDoble de casillas transitables).
        Devuelve: ListaCircular con la ruta.
        """
        inicio = self.laberinto.inicio
        salida = self.laberinto.salida
        mejor = None
        for _ in range(60):
            a = pisos.obtener(self.azar.randrange(pisos.tamano()))
            b = pisos.obtener(self.azar.randrange(pisos.tamano()))
            camino = self.laberinto.camino_mas_corto(a, b)
            if camino is None or camino.tamano() < 4:
                continue
            mejor = camino
            # aceptar solo si ninguna casilla queda cerca del inicio
            seguro = True
            for posicion in camino:
                cerca_inicio = abs(posicion[0] - inicio[0]) + abs(posicion[1] - inicio[1])
                cerca_salida = abs(posicion[0] - salida[0]) + abs(posicion[1] - salida[1])
                if cerca_inicio <= DISTANCIA_SEGURA or cerca_salida <= 2:
                    seguro = False
                    break
            if seguro and camino.tamano() <= 16 and self._se_puede_rodear(camino):
                break
        if mejor is None:  # laberinto diminuto: patrulla en la salida
            mejor = ListaDoble()
            mejor.insertar_final(self.laberinto.salida)
        return construir_ruta_ida_vuelta(mejor)

    def _se_puede_rodear(self, ruta):
        """
        Comprueba que exista un camino del inicio a la salida que NO pase
        por ninguna casilla de la ruta (BFS con casillas bloqueadas). Asi un
        enemigo nunca tapa el unico pasillo hacia la salida.
        Recibe: ruta (ListaDoble de posiciones).
        Devuelve: True si se puede rodear.
        """
        lab = self.laberinto
        bloqueadas = [[False] * lab.ancho for _ in range(lab.alto)]
        for f, c in ruta:
            bloqueadas[f][c] = True
        return lab.camino_mas_corto(lab.inicio, lab.salida, bloqueadas) is not None

    def _liberar_enemigo(self):
        """
        Saca el siguiente enemigo de la COLA de espera y lo pone a patrullar.
        Devuelve: el enemigo liberado o None si no quedan.
        """
        if self.enemigos_espera.esta_vacia():
            return None
        enemigo = self.enemigos_espera.desencolar()
        self.enemigos_activos.insertar_final(enemigo)
        return enemigo

    def hay_enemigo_en(self, posicion):
        """Devuelve True si algun enemigo activo esta en esa casilla. O(e)."""
        for enemigo in self.enemigos_activos:
            if enemigo.posicion == posicion:
                return True
        return False

    # ---------------------------------------------------------- acciones
    def mover(self, direccion):
        """
        Intenta mover al jugador una casilla.
        Recibe: direccion: "arriba", "abajo", "izquierda" o "derecha".
        Devuelve: True si el movimiento se hizo, False si no (pared,
                  direccion invalida o partida terminada). El motivo queda
                  en self.mensaje.
        """
        if self.estado != JUGANDO:
            self.mensaje = "La partida ya terminó."
            return False
        if direccion not in DIRECCIONES:
            self.mensaje = "Dirección no válida."
            return False
        df, dc = DIRECCIONES[direccion]
        destino = (self.jugador[0] + df, self.jugador[1] + dc)
        if not self.laberinto.es_piso(destino):
            self.mensaje = "Hay una pared."
            return False
        self.pila_deshacer.apilar(self.jugador)  # recordar de donde venia
        self.jugador = destino
        self.camino.insertar_final(destino)
        self.mensaje = ""
        self._procesar_turno()
        return True

    def deshacer(self):
        """
        Regresa al jugador a la casilla anterior (desapila). Cuenta como un
        turno, asi que los enemigos tambien se mueven.
        Devuelve: True si pudo deshacer, False si la pila esta vacia.
        """
        if self.estado != JUGANDO:
            self.mensaje = "La partida ya terminó."
            return False
        if self.pila_deshacer.esta_vacia():
            self.mensaje = "No hay movimientos para deshacer."
            return False
        self.jugador = self.pila_deshacer.desapilar()
        self.camino.eliminar_final()  # el paso deshecho sale del camino
        self.deshacer_usados += 1
        self.mensaje = "Movimiento deshecho."
        self._procesar_turno()
        return True

    def esperar(self):
        """
        El jugador se queda quieto un turno (los enemigos si se mueven).
        Sirve para dejar pasar a un enemigo. Cuenta como paso.
        Devuelve: True si se hizo, False si la partida ya termino.
        """
        if self.estado != JUGANDO:
            self.mensaje = "La partida ya terminó."
            return False
        self.mensaje = "Esperaste un turno."
        self._procesar_turno()
        return True

    def pedir_pista(self):
        """
        Calcula con BFS (COLA) el camino mas corto desde el jugador hasta la
        salida y lo deja visible unos turnos.
        Devuelve: True si se dio la pista, False si no quedan pistas.
        """
        if self.estado != JUGANDO:
            return False
        if self.pistas_restantes <= 0:
            self.mensaje = "Ya no te quedan pistas."
            return False
        self.pista = self.laberinto.camino_mas_corto(self.jugador, self.laberinto.salida)
        self.turnos_pista = TURNOS_PISTA
        self.pistas_restantes -= 1
        self.pistas_usadas += 1
        self.mensaje = "Pista: sigue los puntos amarillos (" + str(self.pista.tamano() - 1) + " pasos)."
        return True

    # ------------------------------------------------------------- reglas
    def _procesar_turno(self):
        """
        Aplica las reglas despues de cada accion del jugador:
          1. Si llego a la salida, gana.
          2. Si piso a un enemigo, pierde una vida.
          3. Los enemigos activos avanzan un paso (lista circular).
          4. Si un enemigo lo alcanza, pierde una vida.
          5. Cada 'intervalo' turnos sale un enemigo de la cola de espera.
          6. Si supero el limite de pasos, pierde.
        """
        self.turno += 1
        self.pasos += 1
        if self.turnos_pista > 0:
            self.turnos_pista -= 1
            if self.turnos_pista == 0:
                self.pista = None

        if self.jugador == self.laberinto.salida:
            self.estado = GANO
            self.mensaje = "¡Llegaste a la salida!"
            return

        if self.hay_enemigo_en(self.jugador):
            self._recibir_golpe()
            return

        for enemigo in self.enemigos_activos:
            enemigo.mover()
        if self.hay_enemigo_en(self.jugador):
            self._recibir_golpe()
            return

        if self.turno % self.config["intervalo"] == 0:
            nuevo = self._liberar_enemigo()
            if nuevo is not None:
                self.mensaje = nuevo.nombre + " entró al laberinto."
                if nuevo.posicion == self.jugador:
                    self._recibir_golpe()
                    return

        if self.pasos >= self.limite_pasos:
            self.estado = PERDIO
            self.mensaje = "Se acabaron los pasos."

    def _recibir_golpe(self):
        """
        El jugador pierde una vida. Si le quedan, vuelve al inicio y se
        vacia la pila de deshacer (un golpe no se puede deshacer).
        """
        self.vidas -= 1
        self.golpes += 1
        if self.vidas <= 0:
            self.estado = PERDIO
            self.mensaje = "Te atrapó un enemigo. Sin vidas."
            return
        self.jugador = self.laberinto.inicio
        self.pila_deshacer.vaciar()
        self.camino.insertar_final(self.jugador)
        self.mensaje = "¡Te atraparon! Vuelves al inicio. Vidas: " + str(self.vidas)

    # ------------------------------------------------------------ resultados
    def pasos_restantes(self):
        """Pasos que quedan antes de perder por limite."""
        return max(0, self.limite_pasos - self.pasos)

    def calcular_puntaje(self):
        """
        Puntaje final (solo si gano):
          base de la dificultad + 200 por vida
          - 5 por cada paso de mas sobre el optimo
          - 10 por cada deshacer - 100 por cada pista.
        Devuelve: entero >= 0 (0 si no gano).
        """
        if self.estado != GANO:
            return 0
        extra = max(0, self.pasos - self.pasos_optimos)
        puntaje = (self.config["base"] + 200 * self.vidas - 5 * extra
                   - 10 * self.deshacer_usados - 100 * self.pistas_usadas)
        return max(0, puntaje)


class VisorRecorrido:
    """
    Visor del camino recorrido: navega la LISTA DOBLE nodo por nodo con
    las referencias 'siguiente' y 'anterior' (cada paso es O(1)).
    """

    def __init__(self, camino):
        """
        Recibe: camino (ListaDoble de posiciones, no vacia).
        Devuelve: nada.
        """
        self.camino = camino
        self.nodo = camino.cabeza
        self.indice = 0

    def actual(self):
        """Posicion donde esta el visor."""
        return None if self.nodo is None else self.nodo.dato

    def siguiente(self):
        """Avanza un paso. Devuelve True si pudo avanzar. O(1)."""
        if self.nodo is not None and self.nodo.siguiente is not None:
            self.nodo = self.nodo.siguiente
            self.indice += 1
            return True
        return False

    def anterior(self):
        """Retrocede un paso. Devuelve True si pudo retroceder. O(1)."""
        if self.nodo is not None and self.nodo.anterior is not None:
            self.nodo = self.nodo.anterior
            self.indice -= 1
            return True
        return False

    def ir_inicio(self):
        """Va al primer paso. O(1)."""
        self.nodo = self.camino.cabeza
        self.indice = 0

    def ir_final(self):
        """Va al ultimo paso. O(1)."""
        self.nodo = self.camino.cola
        self.indice = self.camino.tamano() - 1
