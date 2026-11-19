"""
Enemigos que patrullan el laberinto.

Cada enemigo guarda su ruta en una LISTA CIRCULAR: en cada turno avanza al
siguiente nodo y, al llegar al final, la lista lo lleva de nuevo al inicio
sin ningun "if" especial. La ruta es de ida y vuelta (A -> B -> A).
"""

from estructuras.lista_circular import ListaCircular


class Enemigo:
    """Enemigo con una ruta de patrulla circular."""

    def __init__(self, nombre, ruta):
        """
        Crea un enemigo.
        Recibe:
          nombre: texto para identificarlo (ej. "Fantasma 1").
          ruta: ListaCircular de posiciones (fila, columna), no vacia.
        Devuelve: nada.
        """
        if ruta is None or ruta.esta_vacia():
            raise ValueError("la ruta del enemigo no puede estar vacia")
        self.nombre = nombre
        self.ruta = ruta
        self.ruta.reiniciar_cursor()

    @property
    def posicion(self):
        """Posicion actual del enemigo (donde esta el cursor). O(1)."""
        return self.ruta.actual()

    def mover(self):
        """
        Avanza un paso en la ruta circular.
        Recibe: nada.  Devuelve: la nueva posicion.  O(1).
        """
        return self.ruta.avanzar()

    def __str__(self):
        """Texto con nombre y posicion."""
        return self.nombre + " en " + str(self.posicion)


def construir_ruta_ida_vuelta(camino):
    """
    Convierte un camino A -> B (ListaDoble) en una ruta circular de ida y
    vuelta: A, ..., B, ..., (sin repetir A ni B al regresar).
    Ejemplo: camino [1,2,3,4] -> ruta circular (1,2,3,4,3,2) -> se repite.
    Recibe: camino (ListaDoble de posiciones, tamano >= 1).
    Devuelve: ListaCircular.
    Complejidad: O(n). Usa el recorrido hacia atras de la lista doble.
    """
    ruta = ListaCircular()
    for posicion in camino.recorrer_adelante():
        ruta.insertar_final(posicion)
    if camino.tamano() > 2:
        regreso = camino.recorrer_atras()
        next(regreso)  # saltar B (ya esta)
        for i, posicion in enumerate(regreso):
            if i == camino.tamano() - 2:  # no repetir A
                break
            ruta.insertar_final(posicion)
    return ruta
