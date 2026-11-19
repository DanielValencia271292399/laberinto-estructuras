"""
Paquete con las 5 estructuras de datos programadas desde cero.
Ninguna usa list, deque ni otras colecciones de Python: todas se basan en
nodos y referencias.
"""

from estructuras.pila import Pila
from estructuras.cola import Cola
from estructuras.lista_circular import ListaCircular
from estructuras.lista_doble import ListaDoble
from estructuras.arbol_bst import ArbolBST

__all__ = ("Pila", "Cola", "ListaCircular", "ListaDoble", "ArbolBST")
