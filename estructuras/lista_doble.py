"""
Lista doblemente enlazada implementada desde cero.

Cada nodo conoce al anterior y al siguiente, por eso se puede recorrer
hacia adelante y hacia atras.
Uso en el juego:
  - Camino recorrido por el jugador (cada casilla que pisa).
  - Visor de recorrido: al terminar la partida se navega el camino paso a
    paso con las flechas izquierda/derecha.
  - Resultado de los recorridos del arbol de puntajes.
"""


class NodoDoble:
    """Nodo doble: dato, referencia al anterior y al siguiente."""

    def __init__(self, dato):
        """
        Crea un nodo.
        Recibe: dato.  Devuelve: nada.
        """
        self.dato = dato
        self.anterior = None
        self.siguiente = None


class ListaDoble:
    """Lista doble con referencias a la cabeza (inicio) y la cola (final)."""

    def __init__(self):
        """
        Crea una lista vacia.
        Recibe: nada.  Devuelve: nada.
        """
        self.cabeza = None
        self.cola = None
        self._tamano = 0

    # ------------------------------------------------------------ consultas
    def esta_vacia(self):
        """Devuelve True si no hay nodos. O(1)."""
        return self.cabeza is None

    def tamano(self):
        """Devuelve la cantidad de nodos. O(1)."""
        return self._tamano

    def __len__(self):
        """Permite len(lista). O(1)."""
        return self._tamano

    def primero(self):
        """Dato del inicio. Lanza IndexError si esta vacia. O(1)."""
        if self.esta_vacia():
            raise IndexError("lista vacia")
        return self.cabeza.dato

    def ultimo(self):
        """Dato del final. Lanza IndexError si esta vacia. O(1)."""
        if self.esta_vacia():
            raise IndexError("lista vacia")
        return self.cola.dato

    # ----------------------------------------------------------- inserciones
    def insertar_inicio(self, dato):
        """
        Inserta al inicio.
        Recibe: dato.  Devuelve: nada.
        Complejidad: O(1).
        """
        nuevo = NodoDoble(dato)
        if self.esta_vacia():
            self.cabeza = self.cola = nuevo
        else:
            nuevo.siguiente = self.cabeza
            self.cabeza.anterior = nuevo
            self.cabeza = nuevo
        self._tamano += 1

    def insertar_final(self, dato):
        """
        Inserta al final.
        Recibe: dato.  Devuelve: nada.
        Complejidad: O(1).
        """
        nuevo = NodoDoble(dato)
        if self.esta_vacia():
            self.cabeza = self.cola = nuevo
        else:
            nuevo.anterior = self.cola
            self.cola.siguiente = nuevo
            self.cola = nuevo
        self._tamano += 1

    def insertar_en_posicion(self, posicion, dato):
        """
        Inserta en la posicion indicada (0 = inicio, tamano = final).
        Recibe: posicion y dato.  Devuelve: nada.
        Lanza: IndexError si la posicion no es valida.
        Complejidad: O(n).
        """
        if posicion < 0 or posicion > self._tamano:
            raise IndexError("posicion fuera de rango")
        if posicion == 0:
            self.insertar_inicio(dato)
        elif posicion == self._tamano:
            self.insertar_final(dato)
        else:
            siguiente = self._nodo_en(posicion)
            anterior = siguiente.anterior
            nuevo = NodoDoble(dato)
            nuevo.anterior = anterior
            nuevo.siguiente = siguiente
            anterior.siguiente = nuevo
            siguiente.anterior = nuevo
            self._tamano += 1

    # ----------------------------------------------------------- eliminacion
    def eliminar(self, dato):
        """
        Elimina la primera aparicion de 'dato'.
        Recibe: dato.
        Devuelve: True si lo elimino, False si no estaba.
        Complejidad: O(n).
        """
        actual = self.cabeza
        while actual is not None:
            if actual.dato == dato:
                self._desenlazar(actual)
                return True
            actual = actual.siguiente
        return False

    def eliminar_inicio(self):
        """
        Elimina y devuelve el primer dato.
        Lanza IndexError si esta vacia. O(1).
        """
        if self.esta_vacia():
            raise IndexError("lista vacia")
        nodo = self.cabeza
        self._desenlazar(nodo)
        return nodo.dato

    def eliminar_final(self):
        """
        Elimina y devuelve el ultimo dato (se usa al deshacer un paso).
        Lanza IndexError si esta vacia. O(1).
        """
        if self.esta_vacia():
            raise IndexError("lista vacia")
        nodo = self.cola
        self._desenlazar(nodo)
        return nodo.dato

    def eliminar_en_posicion(self, posicion):
        """
        Elimina el nodo de la posicion indicada.
        Recibe: posicion (0..tamano-1).  Devuelve: el dato eliminado.
        Lanza IndexError si no existe. O(n).
        """
        nodo = self._nodo_en(posicion)
        self._desenlazar(nodo)
        return nodo.dato

    def vaciar(self):
        """Elimina todos los nodos. O(1)."""
        self.cabeza = self.cola = None
        self._tamano = 0

    def _desenlazar(self, nodo):
        """
        Saca un nodo de la lista uniendo a sus vecinos (uso interno). O(1).
        """
        if nodo.anterior is None:
            self.cabeza = nodo.siguiente
        else:
            nodo.anterior.siguiente = nodo.siguiente
        if nodo.siguiente is None:
            self.cola = nodo.anterior
        else:
            nodo.siguiente.anterior = nodo.anterior
        nodo.anterior = nodo.siguiente = None
        self._tamano -= 1

    def _nodo_en(self, posicion):
        """
        Devuelve el NODO de la posicion indicada (uso interno).
        Si la posicion esta en la segunda mitad, recorre desde la cola
        hacia atras: asi hace como maximo n/2 pasos.
        Lanza IndexError si no existe. O(n).
        """
        if posicion < 0 or posicion >= self._tamano:
            raise IndexError("posicion fuera de rango")
        if posicion < self._tamano // 2:
            actual = self.cabeza
            for _ in range(posicion):
                actual = actual.siguiente
        else:
            actual = self.cola
            for _ in range(self._tamano - 1 - posicion):
                actual = actual.anterior
        return actual

    # ----------------------------------------------------- busqueda/recorrido
    def buscar(self, dato):
        """
        Busca un dato.
        Recibe: dato.  Devuelve: posicion de la primera aparicion o -1.
        Complejidad: O(n).
        """
        actual = self.cabeza
        i = 0
        while actual is not None:
            if actual.dato == dato:
                return i
            actual = actual.siguiente
            i += 1
        return -1

    def contiene(self, dato):
        """Devuelve True si el dato esta en la lista. O(n)."""
        return self.buscar(dato) != -1

    def obtener(self, posicion):
        """Devuelve el dato de una posicion. O(n)."""
        return self._nodo_en(posicion).dato

    def recorrer_adelante(self):
        """
        Recorre de la cabeza a la cola.
        Devuelve: generador con cada dato. O(n).
        """
        actual = self.cabeza
        while actual is not None:
            yield actual.dato
            actual = actual.siguiente

    def recorrer_atras(self):
        """
        Recorre de la cola a la cabeza (gracias al enlace 'anterior').
        Devuelve: generador con cada dato. O(n).
        """
        actual = self.cola
        while actual is not None:
            yield actual.dato
            actual = actual.anterior

    def __iter__(self):
        """Permite 'for x in lista' (hacia adelante). O(n)."""
        return self.recorrer_adelante()

    def __str__(self):
        """Texto: [a <-> b <-> c]. O(n)."""
        texto = ""
        actual = self.cabeza
        while actual is not None:
            texto += str(actual.dato)
            if actual.siguiente is not None:
                texto += " <-> "
            actual = actual.siguiente
        return "[" + texto + "]"
