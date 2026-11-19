"""
Arbol binario de busqueda (BST) implementado desde cero.

Regla: en cada nodo, las claves menores van a la izquierda y las mayores
o iguales a la derecha.
Uso en el juego:
  - Tabla de mejores puntajes: la clave es el puntaje y el valor es el
    registro de la partida (nombre, dificultad, pasos, fecha).
  - El recorrido inorden inverso entrega el ranking de mayor a menor.
Los recorridos devuelven una ListaDoble (estructura propia).
"""

from estructuras.lista_doble import ListaDoble


class NodoArbol:
    """Nodo del arbol: clave, valor e hijos izquierdo y derecho."""

    def __init__(self, clave, valor):
        """
        Crea un nodo hoja.
        Recibe: clave (comparable, ej. entero) y valor (cualquier objeto).
        Devuelve: nada.
        """
        self.clave = clave
        self.valor = valor
        self.izquierdo = None
        self.derecho = None


class ArbolBST:
    """Arbol binario de busqueda. 'raiz' apunta al nodo superior."""

    def __init__(self):
        """
        Crea un arbol vacio.
        Recibe: nada.  Devuelve: nada.
        """
        self.raiz = None
        self._tamano = 0

    def esta_vacio(self):
        """Devuelve True si el arbol no tiene nodos. O(1)."""
        return self.raiz is None

    def tamano(self):
        """Devuelve la cantidad de nodos. O(1)."""
        return self._tamano

    def __len__(self):
        """Permite len(arbol). O(1)."""
        return self._tamano

    # --------------------------------------------------------------- insertar
    def insertar(self, clave, valor=None):
        """
        Inserta un nodo. Si la clave se repite, el nuevo va a la derecha.
        Recibe: clave y valor.
        Devuelve: nada.
        Complejidad: O(h), h = altura. Promedio O(log n), peor caso O(n).
        Se hace de forma iterativa (sin recursion).
        """
        nuevo = NodoArbol(clave, valor)
        self._tamano += 1
        if self.raiz is None:
            self.raiz = nuevo
            return
        actual = self.raiz
        while True:
            if clave < actual.clave:
                if actual.izquierdo is None:
                    actual.izquierdo = nuevo
                    return
                actual = actual.izquierdo
            else:
                if actual.derecho is None:
                    actual.derecho = nuevo
                    return
                actual = actual.derecho

    # ----------------------------------------------------------------- buscar
    def buscar(self, clave):
        """
        Busca una clave.
        Recibe: clave.
        Devuelve: el valor del primer nodo con esa clave, o None.
        Complejidad: O(h).
        """
        nodo = self._buscar_nodo(clave)
        return None if nodo is None else nodo.valor

    def contiene(self, clave):
        """Devuelve True si existe un nodo con esa clave. O(h)."""
        return self._buscar_nodo(clave) is not None

    def _buscar_nodo(self, clave):
        """Devuelve el nodo con la clave o None (uso interno). O(h)."""
        actual = self.raiz
        while actual is not None:
            if clave == actual.clave:
                return actual
            if clave < actual.clave:
                actual = actual.izquierdo
            else:
                actual = actual.derecho
        return None

    def minimo(self):
        """Devuelve (clave, valor) del menor, o None si esta vacio. O(h)."""
        if self.raiz is None:
            return None
        actual = self.raiz
        while actual.izquierdo is not None:
            actual = actual.izquierdo
        return actual.clave, actual.valor

    def maximo(self):
        """Devuelve (clave, valor) del mayor, o None si esta vacio. O(h)."""
        if self.raiz is None:
            return None
        actual = self.raiz
        while actual.derecho is not None:
            actual = actual.derecho
        return actual.clave, actual.valor

    def altura(self):
        """
        Altura del arbol (vacio = 0, solo raiz = 1).
        Complejidad: O(n), recursivo.
        """
        return self._altura(self.raiz)

    def _altura(self, nodo):
        """Altura de un subarbol (uso interno)."""
        if nodo is None:
            return 0
        return 1 + max(self._altura(nodo.izquierdo), self._altura(nodo.derecho))

    # --------------------------------------------------------------- eliminar
    def eliminar(self, clave, valor=None):
        """
        Elimina un nodo con la clave dada. Si se pasa 'valor', elimina el
        nodo cuya clave Y valor coinciden (sirve cuando hay puntajes repetidos).
        Recibe: clave y opcionalmente valor.
        Devuelve: True si elimino un nodo, False si no lo encontro.
        Complejidad: O(h).

        Casos:
          1) Nodo hoja: se quita.
          2) Nodo con un hijo: el hijo ocupa su lugar.
          3) Nodo con dos hijos: se copia el sucesor inorden (el menor del
             subarbol derecho) y luego se elimina ese sucesor.
        """
        padre = None
        actual = self.raiz
        # 1. Buscar el nodo y su padre
        while actual is not None:
            if clave == actual.clave and (valor is None or actual.valor == valor):
                break
            padre = actual
            if clave < actual.clave:
                actual = actual.izquierdo
            else:
                actual = actual.derecho
        if actual is None:
            return False

        # 2. Caso dos hijos: reemplazar por el sucesor inorden
        if actual.izquierdo is not None and actual.derecho is not None:
            padre_sucesor = actual
            sucesor = actual.derecho
            while sucesor.izquierdo is not None:
                padre_sucesor = sucesor
                sucesor = sucesor.izquierdo
            actual.clave = sucesor.clave
            actual.valor = sucesor.valor
            # ahora hay que quitar el sucesor (tiene a lo sumo un hijo derecho)
            padre = padre_sucesor
            actual = sucesor

        # 3. Caso 0 o 1 hijo
        hijo = actual.izquierdo if actual.izquierdo is not None else actual.derecho
        if padre is None:
            self.raiz = hijo
        elif padre.izquierdo is actual:
            padre.izquierdo = hijo
        else:
            padre.derecho = hijo
        self._tamano -= 1
        return True

    # -------------------------------------------------------------- recorridos
    def inorden(self):
        """
        Recorrido Izquierdo - Raiz - Derecho (claves de menor a mayor).
        Devuelve: ListaDoble con tuplas (clave, valor).  O(n).
        """
        resultado = ListaDoble()
        self._inorden(self.raiz, resultado)
        return resultado

    def _inorden(self, nodo, resultado):
        if nodo is not None:
            self._inorden(nodo.izquierdo, resultado)
            resultado.insertar_final((nodo.clave, nodo.valor))
            self._inorden(nodo.derecho, resultado)

    def preorden(self):
        """
        Recorrido Raiz - Izquierdo - Derecho (sirve para copiar/guardar el
        arbol con la misma forma).
        Devuelve: ListaDoble con tuplas (clave, valor).  O(n).
        """
        resultado = ListaDoble()
        self._preorden(self.raiz, resultado)
        return resultado

    def _preorden(self, nodo, resultado):
        if nodo is not None:
            resultado.insertar_final((nodo.clave, nodo.valor))
            self._preorden(nodo.izquierdo, resultado)
            self._preorden(nodo.derecho, resultado)

    def posorden(self):
        """
        Recorrido Izquierdo - Derecho - Raiz.
        Devuelve: ListaDoble con tuplas (clave, valor).  O(n).
        """
        resultado = ListaDoble()
        self._posorden(self.raiz, resultado)
        return resultado

    def _posorden(self, nodo, resultado):
        if nodo is not None:
            self._posorden(nodo.izquierdo, resultado)
            self._posorden(nodo.derecho, resultado)
            resultado.insertar_final((nodo.clave, nodo.valor))

    def inorden_inverso(self):
        """
        Recorrido Derecho - Raiz - Izquierdo (de mayor a menor): el ranking.
        Devuelve: ListaDoble con tuplas (clave, valor).  O(n).
        """
        resultado = ListaDoble()
        self._inorden_inverso(self.raiz, resultado)
        return resultado

    def _inorden_inverso(self, nodo, resultado):
        if nodo is not None:
            self._inorden_inverso(nodo.derecho, resultado)
            resultado.insertar_final((nodo.clave, nodo.valor))
            self._inorden_inverso(nodo.izquierdo, resultado)
