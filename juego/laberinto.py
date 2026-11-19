"""
Modelo del laberinto: la matriz de paredes, su generacion y la busqueda
del camino mas corto.

  - Generacion: backtracking iterativo con una PILA propia.
  - Camino mas corto: busqueda en anchura (BFS) con una COLA propia.

Representacion: matriz de (2*filas+1) x (2*columnas+1) casillas.
PARED = 1 y PISO = 0. Las celdas "reales" estan en posiciones impares
(1,1), (1,3), ... y entre dos celdas hay una casilla que puede ser pared o
piso (el "pasillo" que las une).

Nota: la matriz es el tablero del juego (acceso directo por fila/columna en
O(1)); no reemplaza a ninguna de las 5 estructuras evaluadas.
"""

import random

from estructuras.pila import Pila
from estructuras.cola import Cola
from estructuras.lista_doble import ListaDoble

PARED = 1
PISO = 0

# Desplazamientos (fila, columna) de cada direccion
DIRECCIONES = {
    "arriba": (-1, 0),
    "abajo": (1, 0),
    "izquierda": (0, -1),
    "derecha": (0, 1),
}


class Laberinto:
    """Laberinto rectangular generado al azar."""

    def __init__(self, filas, columnas, semilla=None, aberturas_extra=0):
        """
        Crea y genera un laberinto.
        Recibe:
          filas, columnas: cantidad de celdas (minimo 2 cada una).
          semilla: numero para repetir el mismo laberinto (opcional).
          aberturas_extra: paredes adicionales que se quitan para crear
                           ciclos (varios caminos posibles).
        Devuelve: nada.
        """
        if filas < 2 or columnas < 2:
            raise ValueError("el laberinto necesita al menos 2x2 celdas")
        self.filas = filas
        self.columnas = columnas
        self.alto = 2 * filas + 1      # casillas de la matriz
        self.ancho = 2 * columnas + 1
        self.azar = random.Random(semilla)
        # matriz llena de paredes
        self.matriz = [[PARED] * self.ancho for _ in range(self.alto)]
        self.inicio = (1, 1)
        self.salida = (self.alto - 2, self.ancho - 2)
        self._generar_con_pila()
        self._abrir_ciclos(aberturas_extra)

    # ------------------------------------------------------------ consultas
    def es_piso(self, posicion):
        """
        Indica si una casilla es transitable.
        Recibe: posicion (fila, columna).
        Devuelve: True si esta dentro del tablero y es piso.  O(1).
        """
        f, c = posicion
        return 0 <= f < self.alto and 0 <= c < self.ancho and self.matriz[f][c] == PISO

    def vecinos(self, posicion):
        """
        Casillas de piso adyacentes (arriba, abajo, izquierda, derecha).
        Recibe: posicion.
        Devuelve: ListaDoble con las posiciones vecinas transitables.  O(1).
        """
        resultado = ListaDoble()
        f, c = posicion
        for df, dc in DIRECCIONES.values():
            vecino = (f + df, c + dc)
            if self.es_piso(vecino):
                resultado.insertar_final(vecino)
        return resultado

    def celdas_de_piso(self):
        """
        Todas las casillas transitables.
        Devuelve: ListaDoble de posiciones.  O(alto*ancho).
        """
        resultado = ListaDoble()
        for f in range(self.alto):
            for c in range(self.ancho):
                if self.matriz[f][c] == PISO:
                    resultado.insertar_final((f, c))
        return resultado

    # ------------------------------------------------- generacion con PILA
    def _generar_con_pila(self):
        """
        Genera el laberinto con backtracking (DFS iterativo):
          1. Se apila la celda inicial y se marca como visitada.
          2. Mientras la pila no este vacia se mira el tope:
             - si tiene celdas vecinas sin visitar, se elige una al azar,
               se rompe la pared entre ambas y se apila la nueva;
             - si no tiene, se desapila (se "devuelve" = backtracking).
        Resultado: un laberinto "perfecto" (un solo camino entre 2 celdas).
        Complejidad: O(filas*columnas): cada celda se apila y desapila 1 vez.
        """
        visitada = [[False] * self.ancho for _ in range(self.alto)]
        pila = Pila()
        f0, c0 = self.inicio
        self.matriz[f0][c0] = PISO
        visitada[f0][c0] = True
        pila.apilar(self.inicio)

        while not pila.esta_vacia():
            f, c = pila.ver_tope()
            # candidatas: celdas a 2 casillas de distancia sin visitar
            candidatas = ListaDoble()
            for df, dc in DIRECCIONES.values():
                nf, nc = f + 2 * df, c + 2 * dc
                if 0 < nf < self.alto - 1 and 0 < nc < self.ancho - 1 and not visitada[nf][nc]:
                    candidatas.insertar_final((nf, nc, df, dc))
            if candidatas.esta_vacia():
                pila.desapilar()  # callejon sin salida: retroceder
                continue
            nf, nc, df, dc = candidatas.obtener(self.azar.randrange(candidatas.tamano()))
            self.matriz[f + df][c + dc] = PISO  # romper la pared intermedia
            self.matriz[nf][nc] = PISO
            visitada[nf][nc] = True
            pila.apilar((nf, nc))

    def _abrir_ciclos(self, cantidad):
        """
        Quita 'cantidad' paredes internas al azar que separan dos pisos,
        para que existan rutas alternativas (y asi esquivar enemigos).
        Recibe: cantidad (entero).  Devuelve: nada.
        """
        intentos = 0
        abiertas = 0
        while abiertas < cantidad and intentos < cantidad * 50:
            intentos += 1
            f = self.azar.randrange(1, self.alto - 1)
            c = self.azar.randrange(1, self.ancho - 1)
            if self.matriz[f][c] != PARED:
                continue
            horizontal = f % 2 == 1 and c % 2 == 0  # pared entre izq y der
            vertical = f % 2 == 0 and c % 2 == 1    # pared entre arriba y abajo
            if horizontal or vertical:
                self.matriz[f][c] = PISO
                abiertas += 1

    # ---------------------------------------------- camino mas corto con COLA
    def camino_mas_corto(self, origen, destino, bloqueadas=None):
        """
        Busqueda en anchura (BFS):
          1. Se encola el origen.
          2. Se desencola una casilla y se encolan sus vecinos no visitados,
             recordando de donde se llego a cada uno (matriz 'padre').
          3. Al desencolar el destino se reconstruye el camino hacia atras.
        Como la cola procesa por "capas" de distancia, el primer camino que
        llega al destino es el MAS CORTO.
        Recibe: origen y destino (posiciones) y, opcionalmente, 'bloqueadas':
                una matriz de True/False del mismo tamano con casillas que no
                se pueden usar (se usa para validar rutas de enemigos).
        Devuelve: ListaDoble con el camino [origen, ..., destino] o None si
                  no hay camino.
        Complejidad: O(V + E) = O(alto*ancho).
        """
        if not self.es_piso(origen) or not self.es_piso(destino):
            return None
        padre = [[None] * self.ancho for _ in range(self.alto)]
        visitada = [[False] * self.ancho for _ in range(self.alto)]
        cola = Cola()
        cola.encolar(origen)
        visitada[origen[0]][origen[1]] = True

        while not cola.esta_vacia():
            actual = cola.desencolar()
            if actual == destino:
                camino = ListaDoble()
                paso = destino
                while paso is not None:  # reconstruir de atras hacia adelante
                    camino.insertar_inicio(paso)
                    paso = padre[paso[0]][paso[1]]
                return camino
            for vecino in self.vecinos(actual):
                vf, vc = vecino
                if not visitada[vf][vc] and (bloqueadas is None or not bloqueadas[vf][vc]):
                    visitada[vf][vc] = True
                    padre[vf][vc] = actual
                    cola.encolar(vecino)
        return None

    def distancia(self, origen, destino):
        """
        Pasos minimos entre dos casillas (usa BFS).
        Devuelve: entero, o -1 si no hay camino.
        """
        camino = self.camino_mas_corto(origen, destino)
        return -1 if camino is None else camino.tamano() - 1
