"""
Lista circular simplemente enlazada, implementada desde cero.

El ultimo nodo apunta de nuevo al primero, por eso se puede recorrer
"una y otra vez" sin llegar nunca a un None.
Uso en el juego:
  - Ruta de patrulla de cada enemigo: el enemigo avanza al siguiente nodo
    en cada turno y, al terminar la ruta, vuelve a empezar sola.
"""


class NodoCircular:
    """Nodo de la lista circular: dato y referencia al siguiente."""

    def __init__(self, dato):
        """
        Crea un nodo.
        Recibe: dato.  Devuelve: nada.
        """
        self.dato = dato
        self.siguiente = None


class ListaCircular:
    """
    Lista circular. Solo se guarda la referencia al ultimo nodo, porque
    desde el ultimo se llega al primero en O(1): primero = ultimo.siguiente.
    Ademas tiene un 'cursor' para recorrerla de forma infinita con avanzar().
    """

    def __init__(self):
        """
        Crea una lista circular vacia.
        Recibe: nada.  Devuelve: nada.
        """
        self.ultimo = None
        self.cursor = None  # nodo "actual" para avanzar() en ciclo
        self._tamano = 0

    # ------------------------------------------------------------ consultas
    def esta_vacia(self):
        """Devuelve True si no hay nodos. O(1)."""
        return self.ultimo is None

    def tamano(self):
        """Devuelve la cantidad de nodos. O(1)."""
        return self._tamano

    def __len__(self):
        """Permite len(lista). O(1)."""
        return self._tamano

    def primero(self):
        """
        Devuelve el dato del primer nodo.
        Lanza IndexError si esta vacia. O(1).
        """
        if self.esta_vacia():
            raise IndexError("lista circular vacia")
        return self.ultimo.siguiente.dato

    # ----------------------------------------------------------- inserciones
    def insertar_inicio(self, dato):
        """
        Inserta un dato al inicio.
        Recibe: dato.  Devuelve: nada.
        Complejidad: O(1).
        """
        nuevo = NodoCircular(dato)
        if self.esta_vacia():
            nuevo.siguiente = nuevo  # un solo nodo se apunta a si mismo
            self.ultimo = nuevo
            self.cursor = nuevo
        else:
            nuevo.siguiente = self.ultimo.siguiente  # apunta al antiguo primero
            self.ultimo.siguiente = nuevo
        self._tamano += 1

    def insertar_final(self, dato):
        """
        Inserta un dato al final.
        Recibe: dato.  Devuelve: nada.
        Complejidad: O(1): se inserta al inicio y se mueve 'ultimo'.
        """
        self.insertar_inicio(dato)
        self.ultimo = self.ultimo.siguiente  # el nuevo pasa a ser el ultimo

    def insertar_en_posicion(self, posicion, dato):
        """
        Inserta un dato en la posicion indicada (0 = inicio).
        Recibe: posicion (0..tamano) y dato.  Devuelve: nada.
        Lanza: IndexError si la posicion no es valida.
        Complejidad: O(n).
        """
        if posicion < 0 or posicion > self._tamano:
            raise IndexError("posicion fuera de rango")
        if posicion == 0:
            self.insertar_inicio(dato)
            return
        if posicion == self._tamano:
            self.insertar_final(dato)
            return
        anterior = self.ultimo.siguiente  # nodo en posicion 0
        for _ in range(posicion - 1):
            anterior = anterior.siguiente
        nuevo = NodoCircular(dato)
        nuevo.siguiente = anterior.siguiente
        anterior.siguiente = nuevo
        self._tamano += 1

    # ----------------------------------------------------------- eliminacion
    def eliminar(self, dato):
        """
        Elimina la primera aparicion de 'dato'.
        Recibe: dato a eliminar.
        Devuelve: True si lo elimino, False si no estaba.
        Complejidad: O(n).
        """
        if self.esta_vacia():
            return False
        anterior = self.ultimo
        actual = self.ultimo.siguiente
        for _ in range(self._tamano):
            if actual.dato == dato:
                self._desenlazar(anterior, actual)
                return True
            anterior = actual
            actual = actual.siguiente
        return False

    def eliminar_en_posicion(self, posicion):
        """
        Elimina el nodo de la posicion indicada.
        Recibe: posicion (0..tamano-1).
        Devuelve: el dato eliminado.
        Lanza: IndexError si la posicion no es valida.
        Complejidad: O(n).
        """
        if posicion < 0 or posicion >= self._tamano:
            raise IndexError("posicion fuera de rango")
        anterior = self.ultimo
        actual = self.ultimo.siguiente
        for _ in range(posicion):
            anterior = actual
            actual = actual.siguiente
        self._desenlazar(anterior, actual)
        return actual.dato

    def _desenlazar(self, anterior, actual):
        """
        Saca 'actual' de la lista (uso interno).
        Recibe: el nodo anterior y el nodo a quitar.  Devuelve: nada.  O(1).
        """
        if self._tamano == 1:
            self.ultimo = None
            self.cursor = None
        else:
            anterior.siguiente = actual.siguiente
            if actual is self.ultimo:
                self.ultimo = anterior
            if actual is self.cursor:
                self.cursor = actual.siguiente
        self._tamano -= 1

    # ----------------------------------------------------- busqueda/recorrido
    def buscar(self, dato):
        """
        Busca un dato.
        Recibe: dato.
        Devuelve: la posicion (0..n-1) de la primera aparicion, o -1.
        Complejidad: O(n).
        """
        if self.esta_vacia():
            return -1
        actual = self.ultimo.siguiente
        for i in range(self._tamano):
            if actual.dato == dato:
                return i
            actual = actual.siguiente
        return -1

    def obtener(self, posicion):
        """
        Devuelve el dato en la posicion indicada.
        Lanza IndexError si no existe. O(n).
        """
        if posicion < 0 or posicion >= self._tamano:
            raise IndexError("posicion fuera de rango")
        actual = self.ultimo.siguiente
        for _ in range(posicion):
            actual = actual.siguiente
        return actual.dato

    def recorrer(self, vueltas=1):
        """
        Recorre la lista desde el primero, dando 'vueltas' vueltas completas.
        Recibe: vueltas (entero >= 1).
        Devuelve: un generador que entrega cada dato.
        Complejidad: O(n * vueltas).
        """
        if self.esta_vacia():
            return
        actual = self.ultimo.siguiente
        for _ in range(self._tamano * vueltas):
            yield actual.dato
            actual = actual.siguiente

    def __iter__(self):
        """Permite 'for x in lista' (una vuelta). O(n)."""
        return self.recorrer(1)

    # -------------------------------------------------------- cursor en ciclo
    def actual(self):
        """
        Devuelve el dato donde esta el cursor (o None si esta vacia). O(1).
        """
        return None if self.cursor is None else self.cursor.dato

    def avanzar(self):
        """
        Mueve el cursor al siguiente nodo. Al pasar el ultimo, vuelve al
        primero automaticamente (por ser circular).
        Recibe: nada.
        Devuelve: el nuevo dato del cursor (o None si esta vacia).
        Complejidad: O(1).
        """
        if self.cursor is None:
            return None
        self.cursor = self.cursor.siguiente
        return self.cursor.dato

    def reiniciar_cursor(self):
        """Pone el cursor en el primer nodo. O(1)."""
        self.cursor = None if self.ultimo is None else self.ultimo.siguiente

    def __str__(self):
        """Texto de la lista: (a -> b -> c -> ...). O(n)."""
        texto = ""
        for dato in self.recorrer(1):
            texto += str(dato) + " -> "
        return "(" + texto + "...)"
