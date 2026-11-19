"""
Cola (queue) implementada desde cero con nodos enlazados.

Regla FIFO: el primero que entra es el primero que sale.
Uso en el juego:
  - Busqueda en anchura (BFS) para hallar el camino mas corto (pista y
    calculo de pasos optimos).
  - Enemigos en espera: salen al laberinto uno por uno, en orden de llegada.
"""


class NodoCola:
    """Nodo de la cola: guarda un dato y la referencia al nodo de atras."""

    def __init__(self, dato):
        """
        Crea un nodo.
        Recibe: dato a guardar.  Devuelve: nada.
        """
        self.dato = dato
        self.siguiente = None


class Cola:
    """Cola enlazada con referencias al frente (salida) y al final (entrada)."""

    def __init__(self):
        """
        Crea una cola vacia.
        Recibe: nada.  Devuelve: nada.
        """
        self.frente = None
        self.final = None
        self._tamano = 0

    def encolar(self, dato):
        """
        Agrega un elemento al final de la cola (enqueue).
        Recibe: dato a guardar.
        Devuelve: nada.
        Complejidad: O(1) gracias a la referencia 'final'.
        """
        nuevo = NodoCola(dato)
        if self.esta_vacia():
            self.frente = nuevo
        else:
            self.final.siguiente = nuevo
        self.final = nuevo
        self._tamano += 1

    def desencolar(self):
        """
        Saca y devuelve el elemento del frente (dequeue).
        Recibe: nada.
        Devuelve: el dato del frente.
        Lanza: IndexError si la cola esta vacia.
        Complejidad: O(1).
        """
        if self.esta_vacia():
            raise IndexError("desencolar de una cola vacia")
        dato = self.frente.dato
        self.frente = self.frente.siguiente
        if self.frente is None:  # quedo vacia: el final tambien se limpia
            self.final = None
        self._tamano -= 1
        return dato

    def ver_frente(self):
        """
        Consulta el elemento del frente sin sacarlo.
        Recibe: nada.
        Devuelve: el dato del frente.
        Lanza: IndexError si la cola esta vacia.
        Complejidad: O(1).
        """
        if self.esta_vacia():
            raise IndexError("ver_frente de una cola vacia")
        return self.frente.dato

    def esta_vacia(self):
        """
        Indica si la cola no tiene elementos.
        Recibe: nada.  Devuelve: True/False.
        Complejidad: O(1).
        """
        return self.frente is None

    def tamano(self):
        """
        Cantidad de elementos.
        Recibe: nada.  Devuelve: entero.
        Complejidad: O(1).
        """
        return self._tamano

    def __len__(self):
        """Permite usar len(cola). O(1)."""
        return self._tamano

    def __str__(self):
        """
        Texto del frente al final. Ej: frente-> [1, 2, 3] <-final.
        Complejidad: O(n).
        """
        partes = ""
        actual = self.frente
        while actual is not None:
            partes += str(actual.dato)
            if actual.siguiente is not None:
                partes += ", "
            actual = actual.siguiente
        return "frente-> [" + partes + "] <-final"
