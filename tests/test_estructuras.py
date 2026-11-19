"""
Pruebas unitarias de las 5 estructuras de datos propias.
Ejecutar desde la carpeta del proyecto:  python -m unittest -v
"""

import ast
import os
import unittest

from estructuras.pila import Pila
from estructuras.cola import Cola
from estructuras.lista_circular import ListaCircular
from estructuras.lista_doble import ListaDoble
from estructuras.arbol_bst import ArbolBST


def a_texto(iterable):
    """Convierte un recorrido en texto 'a,b,c' para comparar facilmente."""
    texto = ""
    for dato in iterable:
        texto += ("," if texto else "") + str(dato)
    return texto


class PruebasPila(unittest.TestCase):
    def test_lifo(self):
        pila = Pila()
        for i in range(1, 4):
            pila.apilar(i)
        self.assertEqual(pila.tamano(), 3)
        self.assertEqual(pila.ver_tope(), 3)
        self.assertEqual(pila.desapilar(), 3)
        self.assertEqual(pila.desapilar(), 2)
        self.assertEqual(pila.tamano(), 1)
        self.assertFalse(pila.esta_vacia())
        self.assertEqual(pila.desapilar(), 1)
        self.assertTrue(pila.esta_vacia())

    def test_vacia_lanza_error(self):
        pila = Pila()
        with self.assertRaises(IndexError):
            pila.desapilar()
        with self.assertRaises(IndexError):
            pila.ver_tope()

    def test_vaciar(self):
        pila = Pila()
        pila.apilar("a")
        pila.vaciar()
        self.assertTrue(pila.esta_vacia())
        self.assertEqual(len(pila), 0)


class PruebasCola(unittest.TestCase):
    def test_fifo(self):
        cola = Cola()
        for letra in "abc":
            cola.encolar(letra)
        self.assertEqual(cola.tamano(), 3)
        self.assertEqual(cola.ver_frente(), "a")
        self.assertEqual(cola.desencolar(), "a")
        self.assertEqual(cola.desencolar(), "b")
        cola.encolar("d")
        self.assertEqual(cola.desencolar(), "c")
        self.assertEqual(cola.desencolar(), "d")
        self.assertTrue(cola.esta_vacia())

    def test_final_se_limpia(self):
        cola = Cola()
        cola.encolar(1)
        cola.desencolar()
        self.assertIsNone(cola.final)
        cola.encolar(2)  # debe seguir funcionando despues de vaciarse
        self.assertEqual(cola.ver_frente(), 2)

    def test_vacia_lanza_error(self):
        with self.assertRaises(IndexError):
            Cola().desencolar()
        with self.assertRaises(IndexError):
            Cola().ver_frente()


class PruebasListaCircular(unittest.TestCase):
    def setUp(self):
        self.lista = ListaCircular()
        self.lista.insertar_final("B")
        self.lista.insertar_inicio("A")
        self.lista.insertar_final("D")
        self.lista.insertar_en_posicion(2, "C")  # A B C D

    def test_inserciones(self):
        self.assertEqual(a_texto(self.lista.recorrer()), "A,B,C,D")
        self.assertEqual(self.lista.tamano(), 4)

    def test_es_circular(self):
        self.assertIs(self.lista.ultimo.siguiente.dato, "A")
        self.assertEqual(a_texto(self.lista.recorrer(2)), "A,B,C,D,A,B,C,D")

    def test_avanzar_da_la_vuelta(self):
        self.lista.reiniciar_cursor()
        vistos = ""
        for _ in range(6):
            vistos += self.lista.avanzar()
        self.assertEqual(vistos, "BCDABC")

    def test_buscar_y_eliminar(self):
        self.assertEqual(self.lista.buscar("C"), 2)
        self.assertEqual(self.lista.buscar("Z"), -1)
        self.assertTrue(self.lista.eliminar("A"))   # eliminar el primero
        self.assertTrue(self.lista.eliminar("D"))   # eliminar el ultimo
        self.assertFalse(self.lista.eliminar("Z"))
        self.assertEqual(a_texto(self.lista.recorrer()), "B,C")
        self.assertEqual(self.lista.ultimo.siguiente.dato, "B")
        self.assertEqual(self.lista.eliminar_en_posicion(1), "C")
        self.assertEqual(self.lista.eliminar_en_posicion(0), "B")
        self.assertTrue(self.lista.esta_vacia())

    def test_posicion_invalida(self):
        with self.assertRaises(IndexError):
            self.lista.insertar_en_posicion(9, "X")
        with self.assertRaises(IndexError):
            self.lista.eliminar_en_posicion(-1)


class PruebasListaDoble(unittest.TestCase):
    def setUp(self):
        self.lista = ListaDoble()
        for n in (2, 3, 5):
            self.lista.insertar_final(n)
        self.lista.insertar_inicio(1)
        self.lista.insertar_en_posicion(3, 4)  # 1 2 3 4 5

    def test_recorridos_en_ambos_sentidos(self):
        self.assertEqual(a_texto(self.lista.recorrer_adelante()), "1,2,3,4,5")
        self.assertEqual(a_texto(self.lista.recorrer_atras()), "5,4,3,2,1")

    def test_enlaces_correctos(self):
        nodo = self.lista.cabeza
        while nodo.siguiente is not None:
            self.assertIs(nodo.siguiente.anterior, nodo)
            nodo = nodo.siguiente
        self.assertIs(nodo, self.lista.cola)

    def test_buscar_obtener(self):
        self.assertEqual(self.lista.buscar(4), 3)
        self.assertEqual(self.lista.buscar(9), -1)
        self.assertEqual(self.lista.obtener(4), 5)  # se busca desde la cola

    def test_eliminaciones(self):
        self.assertTrue(self.lista.eliminar(3))
        self.assertEqual(self.lista.eliminar_inicio(), 1)
        self.assertEqual(self.lista.eliminar_final(), 5)
        self.assertEqual(self.lista.eliminar_en_posicion(1), 4)
        self.assertEqual(a_texto(self.lista), "2")
        self.assertEqual(self.lista.eliminar_final(), 2)
        self.assertTrue(self.lista.esta_vacia())
        self.assertIsNone(self.lista.cola)
        with self.assertRaises(IndexError):
            self.lista.eliminar_final()


class PruebasArbolBST(unittest.TestCase):
    def setUp(self):
        self.arbol = ArbolBST()
        for clave in (50, 30, 70, 20, 40, 60, 80):
            self.arbol.insertar(clave, "v" + str(clave))

    def claves(self, recorrido):
        return a_texto(clave for clave, _ in recorrido)

    def test_recorridos(self):
        self.assertEqual(self.claves(self.arbol.inorden()), "20,30,40,50,60,70,80")
        self.assertEqual(self.claves(self.arbol.preorden()), "50,30,20,40,70,60,80")
        self.assertEqual(self.claves(self.arbol.posorden()), "20,40,30,60,80,70,50")
        self.assertEqual(self.claves(self.arbol.inorden_inverso()), "80,70,60,50,40,30,20")

    def test_buscar(self):
        self.assertEqual(self.arbol.buscar(60), "v60")
        self.assertIsNone(self.arbol.buscar(65))
        self.assertEqual(self.arbol.minimo()[0], 20)
        self.assertEqual(self.arbol.maximo()[0], 80)
        self.assertEqual(self.arbol.altura(), 3)

    def test_eliminar_hoja_un_hijo_dos_hijos(self):
        self.assertTrue(self.arbol.eliminar(20))   # hoja
        self.arbol.insertar(65, "v65")
        self.assertTrue(self.arbol.eliminar(60))   # un hijo
        self.assertTrue(self.arbol.eliminar(50))   # dos hijos (la raiz)
        self.assertFalse(self.arbol.eliminar(999))
        self.assertEqual(self.claves(self.arbol.inorden()), "30,40,65,70,80")
        self.assertEqual(self.arbol.raiz.clave, 65)
        self.assertEqual(self.arbol.tamano(), 5)

    def test_claves_repetidas(self):
        self.arbol.insertar(50, "otro")
        self.assertEqual(self.arbol.tamano(), 8)
        self.assertTrue(self.arbol.eliminar(50, "otro"))  # elimina el exacto
        self.assertEqual(self.arbol.buscar(50), "v50")

    def test_eliminar_hasta_vaciar(self):
        for clave in (50, 30, 70, 20, 40, 60, 80):
            self.assertTrue(self.arbol.eliminar(clave))
        self.assertTrue(self.arbol.esta_vacio())


class PruebasSinColeccionesDePython(unittest.TestCase):
    """
    Revisa el codigo de las estructuras (con el modulo ast, que lee el
    codigo como arbol sintactico) para comprobar que NO usan listas,
    diccionarios, conjuntos, deque ni el modulo queue.
    """

    def test_codigo_fuente(self):
        carpeta = os.path.join(os.path.dirname(__file__), "..", "estructuras")
        prohibidas = ("list", "dict", "set", "deque")
        for nombre in os.listdir(carpeta):
            if not nombre.endswith(".py"):
                continue
            with open(os.path.join(carpeta, nombre), encoding="utf-8") as archivo:
                arbol = ast.parse(archivo.read())
            for nodo in ast.walk(arbol):
                donde = nombre + " linea " + str(getattr(nodo, "lineno", "?"))
                self.assertNotIsInstance(nodo, (ast.List, ast.Dict, ast.Set, ast.ListComp,
                                                ast.DictComp, ast.SetComp), donde)
                if isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name):
                    self.assertNotIn(nodo.func.id, prohibidas, donde)
                if isinstance(nodo, (ast.Import, ast.ImportFrom)):
                    modulo = getattr(nodo, "module", None) or nodo.names[0].name
                    self.assertNotIn(modulo, ("collections", "queue"), donde)


if __name__ == "__main__":
    unittest.main()
