"""
Pila (stack) implementada desde cero con nodos enlazados.

Regla LIFO: el ultimo elemento que entra es el primero que sale.
Uso en el juego:
  - Generar el laberinto con backtracking (DFS iterativo).
  - Guardar las posiciones anteriores del jugador para "deshacer" y "rehacer".
"""


class NodoPila:
    """Nodo de la pila: guarda un dato y la referencia al nodo de abajo."""

    def __init__(self, dato):
        """
        Crea un nodo.
        Recibe: dato (cualquier objeto) que se va a guardar.
        Devuelve: nada (constructor).
        """
        self.dato = dato
        self.siguiente = None  # nodo que esta debajo en la pila


class Pila:
    """Pila enlazada. El atributo 'tope' apunta al ultimo elemento apilado."""

    def __init__(self):
        """
        Crea una pila vacia.
        Recibe: nada.  Devuelve: nada.
        """
        self.tope = None
        self._tamano = 0

    def apilar(self, dato):
        """
        Pone un elemento encima de la pila (push).
        Recibe: dato a guardar.
        Devuelve: nada.
        Complejidad: O(1).
        """
        nuevo = NodoPila(dato)
        nuevo.siguiente = self.tope  # el nuevo queda encima del tope actual
        self.tope = nuevo
        self._tamano += 1

    def desapilar(self):
        """
        Saca y devuelve el elemento de encima (pop).
        Recibe: nada.
        Devuelve: el dato del tope.
        Lanza: IndexError si la pila esta vacia.
        Complejidad: O(1).
        """
        if self.esta_vacia():
            raise IndexError("desapilar de una pila vacia")
        dato = self.tope.dato
        self.tope = self.tope.siguiente  # el de abajo pasa a ser el tope
        self._tamano -= 1
        return dato

    def ver_tope(self):
        """
        Consulta el elemento de encima sin sacarlo (peek).
        Recibe: nada.
        Devuelve: el dato del tope.
        Lanza: IndexError si la pila esta vacia.
        Complejidad: O(1).
        """
        if self.esta_vacia():
            raise IndexError("ver_tope de una pila vacia")
        return self.tope.dato

    def esta_vacia(self):
        """
        Indica si la pila no tiene elementos.
        Recibe: nada.  Devuelve: True si esta vacia, False si no.
        Complejidad: O(1).
        """
        return self.tope is None

    def tamano(self):
        """
        Cantidad de elementos en la pila.
        Recibe: nada.  Devuelve: entero.
        Complejidad: O(1) (se lleva un contador).
        """
        return self._tamano

    def vaciar(self):
        """
        Elimina todos los elementos.
        Recibe: nada.  Devuelve: nada.
        Complejidad: O(1) (el recolector de basura libera los nodos).
        """
        self.tope = None
        self._tamano = 0

    def __len__(self):
        """Permite usar len(pila). Devuelve el tamano. O(1)."""
        return self._tamano

    def __str__(self):
        """
        Representacion en texto, del tope hacia abajo. Ej: [3, 2, 1>.
        Complejidad: O(n).
        """
        partes = ""
        actual = self.tope
        while actual is not None:
            partes += str(actual.dato)
            if actual.siguiente is not None:
                partes += ", "
            actual = actual.siguiente
        return "tope-> [" + partes + "]"
