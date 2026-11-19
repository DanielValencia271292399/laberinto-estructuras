"""
Pruebas de la logica del juego (sin interfaz grafica).
Ejecutar desde la carpeta del proyecto:  python -m unittest -v
"""

import os
import tempfile
import unittest

from estructuras.lista_doble import ListaDoble
from juego.laberinto import Laberinto, PISO
from juego.enemigo import Enemigo, construir_ruta_ida_vuelta
from juego.partida import Partida, VisorRecorrido, GANO, PERDIO, JUGANDO, DIFICULTADES
from juego.puntajes import TablaPuntajes, Registro, validar_nombre, validar_puntaje

DIRECCION = {(-1, 0): "arriba", (1, 0): "abajo", (0, -1): "izquierda", (0, 1): "derecha"}


def direccion_hacia(origen, destino):
    """Direccion para ir de una casilla a otra vecina."""
    return DIRECCION[(destino[0] - origen[0], destino[1] - origen[1])]


def jugar_esquivando(partida, maximo=3000):
    """
    'Bot' que juega con cuidado, como lo haria una persona: en cada turno
    elige la primera accion segura entre (1) avanzar por el camino mas
    corto (BFS) que rodea a los enemigos, (2) esperar y (3) apartarse a
    otra casilla vecina.
    Una casilla es segura si ningun enemigo esta ahi ni va a estar ahi en el
    siguiente turno. Sirve para comprobar que el juego se puede ganar.
    """
    for _ in range(maximo):
        if partida.estado != JUGANDO:
            break

        def segura(casilla):
            for enemigo in partida.enemigos_activos:
                if casilla in (enemigo.posicion, enemigo.ruta.cursor.siguiente.dato):
                    return False
            return True

        # BFS evitando las casillas por donde pasaran los enemigos pronto
        lab = partida.laberinto
        bloqueadas = [[False] * lab.ancho for _ in range(lab.alto)]
        for enemigo in partida.enemigos_activos:
            nodo = enemigo.ruta.cursor
            for _ in range(3):
                bloqueadas[nodo.dato[0]][nodo.dato[1]] = True
                nodo = nodo.siguiente
        camino = lab.camino_mas_corto(partida.jugador, lab.salida, bloqueadas)
        if camino is None:
            camino = lab.camino_mas_corto(partida.jugador, lab.salida)
        siguiente = camino.obtener(1)
        if segura(siguiente):
            partida.mover(direccion_hacia(partida.jugador, siguiente))
        elif segura(partida.jugador):
            partida.esperar()
        else:
            movido = False
            for vecino in partida.laberinto.vecinos(partida.jugador):
                if segura(vecino):
                    partida.mover(direccion_hacia(partida.jugador, vecino))
                    movido = True
                    break
            if not movido:
                partida.esperar()
    return partida


class PruebasLaberinto(unittest.TestCase):
    def test_laberinto_perfecto_conectado(self):
        lab = Laberinto(10, 12, semilla=1)
        # todas las celdas impares son piso y alcanzables desde el inicio
        for f in range(1, lab.alto, 2):
            for c in range(1, lab.ancho, 2):
                self.assertEqual(lab.matriz[f][c], PISO)
                self.assertNotEqual(lab.distancia(lab.inicio, (f, c)), -1)
        # laberinto perfecto: pisos = 2*celdas - 1  (arbol de expansion)
        self.assertEqual(lab.celdas_de_piso().tamano(), 2 * 10 * 12 - 1)

    def test_bordes_son_pared(self):
        lab = Laberinto(5, 5, semilla=2)
        for c in range(lab.ancho):
            self.assertFalse(lab.es_piso((0, c)))
            self.assertFalse(lab.es_piso((lab.alto - 1, c)))

    def test_misma_semilla_mismo_laberinto(self):
        self.assertEqual(Laberinto(8, 8, semilla=5).matriz, Laberinto(8, 8, semilla=5).matriz)

    def test_bfs_camino_valido_y_minimo(self):
        lab = Laberinto(8, 8, semilla=3, aberturas_extra=10)
        camino = lab.camino_mas_corto(lab.inicio, lab.salida)
        self.assertEqual(camino.primero(), lab.inicio)
        self.assertEqual(camino.ultimo(), lab.salida)
        anterior = None
        for paso in camino:  # cada paso es vecino del anterior y es piso
            self.assertTrue(lab.es_piso(paso))
            if anterior is not None:
                self.assertEqual(abs(paso[0] - anterior[0]) + abs(paso[1] - anterior[1]), 1)
            anterior = paso
        # minimo: nunca menor que la distancia Manhattan
        manhattan = (lab.salida[0] - lab.inicio[0]) + (lab.salida[1] - lab.inicio[1])
        self.assertGreaterEqual(camino.tamano() - 1, manhattan)

    def test_bfs_sin_camino(self):
        lab = Laberinto(3, 3, semilla=1)
        self.assertIsNone(lab.camino_mas_corto(lab.inicio, (0, 0)))  # (0,0) es pared

    def test_tamano_invalido(self):
        with self.assertRaises(ValueError):
            Laberinto(1, 5)


class PruebasEnemigo(unittest.TestCase):
    def test_ruta_ida_y_vuelta(self):
        camino = ListaDoble()
        for n in (1, 2, 3, 4):
            camino.insertar_final(n)
        ruta = construir_ruta_ida_vuelta(camino)
        texto = ""
        for dato in ruta.recorrer(2):
            texto += str(dato)
        self.assertEqual(texto, "123432123432")

    def test_enemigo_patrulla_en_ciclo(self):
        camino = ListaDoble()
        for n in ("a", "b", "c"):
            camino.insertar_final(n)
        enemigo = Enemigo("E", construir_ruta_ida_vuelta(camino))  # a b c b
        visitas = enemigo.posicion
        for _ in range(5):
            visitas += enemigo.mover()
        self.assertEqual(visitas, "abcbab")

    def test_ruta_vacia_invalida(self):
        with self.assertRaises(ValueError):
            Enemigo("E", construir_ruta_ida_vuelta(ListaDoble()))


class PruebasPartida(unittest.TestCase):
    def nueva(self, dificultad="Facil", semilla=10):
        return Partida("Prueba", dificultad, semilla=semilla)

    def test_estado_inicial(self):
        p = self.nueva()
        self.assertEqual(p.estado, JUGANDO)
        self.assertEqual(p.jugador, p.laberinto.inicio)
        self.assertEqual(p.vidas, 3)
        self.assertEqual(p.enemigos_espera.tamano(), DIFICULTADES["Facil"]["enemigos"])
        self.assertTrue(p.enemigos_activos.esta_vacia())
        self.assertEqual(p.camino.tamano(), 1)

    def test_no_atraviesa_paredes(self):
        p = self.nueva()
        self.assertFalse(p.mover("arriba"))  # arriba del inicio hay borde
        self.assertEqual(p.mensaje, "Hay una pared.")
        self.assertEqual(p.pasos, 0)

    def test_direccion_invalida_no_rompe(self):
        p = self.nueva()
        self.assertFalse(p.mover("diagonal"))
        self.assertFalse(p.mover(None))
        self.assertEqual(p.estado, JUGANDO)

    def test_mover_y_deshacer(self):
        p = self.nueva()
        vecino = p.laberinto.vecinos(p.jugador).obtener(0)
        self.assertTrue(p.mover(direccion_hacia(p.jugador, vecino)))
        self.assertEqual(p.pila_deshacer.tamano(), 1)
        self.assertEqual(p.camino.tamano(), 2)
        self.assertTrue(p.deshacer())
        self.assertEqual(p.jugador, p.laberinto.inicio)
        self.assertEqual(p.camino.tamano(), 1)
        self.assertFalse(p.deshacer())  # pila vacia
        self.assertEqual(p.deshacer_usados, 1)

    def test_enemigos_salen_de_la_cola(self):
        p = self.nueva()
        intervalo = p.config["intervalo"]
        vecino = p.laberinto.vecinos(p.jugador).obtener(0)
        ida = direccion_hacia(p.jugador, vecino)
        vuelta = direccion_hacia(vecino, p.jugador)
        for i in range(intervalo):
            p.mover(ida if i % 2 == 0 else vuelta)
        self.assertEqual(p.enemigos_activos.tamano(), 1)
        self.assertEqual(p.enemigos_espera.tamano(), p.config["enemigos"] - 1)

    def test_pista_bfs(self):
        p = self.nueva()
        self.assertTrue(p.pedir_pista())
        self.assertEqual(p.pista.tamano() - 1, p.pasos_optimos)
        for _ in range(p.config["pistas"] - 1):
            p.pedir_pista()
        self.assertFalse(p.pedir_pista())  # sin pistas

    def test_golpe_quita_vida_y_vuelve_al_inicio(self):
        p = self.nueva()
        p._recibir_golpe()
        self.assertEqual(p.vidas, 2)
        self.assertEqual(p.jugador, p.laberinto.inicio)
        self.assertTrue(p.pila_deshacer.esta_vacia())
        p._recibir_golpe()
        p._recibir_golpe()
        self.assertEqual(p.estado, PERDIO)

    def test_perder_por_limite_de_pasos(self):
        p = self.nueva()
        p.enemigos_espera = type(p.enemigos_espera)()  # sin enemigos
        vecino = p.laberinto.vecinos(p.jugador).obtener(0)
        ida = direccion_hacia(p.jugador, vecino)
        vuelta = direccion_hacia(vecino, p.jugador)
        i = 0
        while p.estado == JUGANDO:
            p.mover(ida if i % 2 == 0 else vuelta)
            i += 1
        self.assertEqual(p.estado, PERDIO)
        self.assertEqual(p.pasos, p.limite_pasos)
        self.assertEqual(p.calcular_puntaje(), 0)

    def test_ganar_por_camino_optimo_sin_enemigos(self):
        p = self.nueva()
        p.enemigos_espera = type(p.enemigos_espera)()
        camino = p.laberinto.camino_mas_corto(p.jugador, p.laberinto.salida)
        nodo = camino.cabeza
        while nodo.siguiente is not None:
            p.mover(direccion_hacia(nodo.dato, nodo.siguiente.dato))
            nodo = nodo.siguiente
        self.assertEqual(p.estado, GANO)
        self.assertEqual(p.pasos, p.pasos_optimos)
        self.assertEqual(p.calcular_puntaje(), 1000 + 3 * 200)
        self.assertFalse(p.mover("abajo"))  # ya termino

    def test_se_puede_ganar_en_todas_las_dificultades(self):
        ganadas = 0
        for dificultad in DIFICULTADES:
            for semilla in range(5):
                if jugar_esquivando(Partida("Bot", dificultad, semilla=semilla)).estado == GANO:
                    ganadas += 1
        self.assertGreaterEqual(ganadas, 14)  # al menos 14 de 15

    def test_esperar(self):
        p = self.nueva()
        self.assertTrue(p.esperar())
        self.assertEqual(p.jugador, p.laberinto.inicio)
        self.assertEqual(p.pasos, 1)
        self.assertEqual(p.camino.tamano(), 1)

    def test_dificultad_invalida(self):
        with self.assertRaises(ValueError):
            Partida("X", "Imposible")

    def test_visor_recorrido(self):
        p = self.nueva()
        vecino = p.laberinto.vecinos(p.jugador).obtener(0)
        p.mover(direccion_hacia(p.jugador, vecino))
        visor = VisorRecorrido(p.camino)
        self.assertEqual(visor.actual(), p.laberinto.inicio)
        self.assertFalse(visor.anterior())
        self.assertTrue(visor.siguiente())
        self.assertEqual(visor.actual(), vecino)
        self.assertFalse(visor.siguiente())
        visor.ir_inicio()
        self.assertEqual(visor.indice, 0)


class PruebasPuntajes(unittest.TestCase):
    def setUp(self):
        self.carpeta = tempfile.mkdtemp()
        self.ruta = os.path.join(self.carpeta, "puntajes.txt")

    def tearDown(self):
        if os.path.exists(self.ruta):
            os.remove(self.ruta)
        os.rmdir(self.carpeta)

    def test_ranking_y_persistencia(self):
        tabla = TablaPuntajes(self.ruta)
        for nombre, puntos in (("Ana", 1500), ("Beto", 2600), ("Caro", 900), ("Dani", 2600)):
            tabla.agregar(Registro(nombre, puntos, "Medio", 100, "2026-11-19 10:00"))
        orden = ""
        for r in tabla.ranking():
            orden += r.nombre + " "
        self.assertEqual(orden, "Dani Beto Ana Caro ")
        recargada = TablaPuntajes(self.ruta)  # se guarda en preorden
        self.assertEqual(recargada.arbol.tamano(), 4)
        self.assertEqual(recargada.arbol.preorden().obtener(0)[0], 1500)  # misma raiz

    def test_eliminar_registro_exacto(self):
        tabla = TablaPuntajes(self.ruta)
        a = Registro("Ana", 1000, "Facil", 50, "f1")
        b = Registro("Beto", 1000, "Facil", 60, "f2")
        tabla.agregar(a)
        tabla.agregar(b)
        self.assertTrue(tabla.eliminar(b))
        self.assertEqual(tabla.buscar(1000).nombre, "Ana")
        self.assertFalse(tabla.eliminar(b))

    def test_archivo_danado_no_rompe(self):
        with open(self.ruta, "w", encoding="utf-8") as archivo:
            archivo.write("basura\nAna;abc;Facil;1;f\nBeto;1200;Facil;40;2026-11-19 10:00\n")
        tabla = TablaPuntajes(self.ruta)
        self.assertEqual(tabla.arbol.tamano(), 1)

    def test_validaciones(self):
        self.assertEqual(validar_nombre("  Daniel  "), (True, "Daniel"))
        self.assertFalse(validar_nombre("")[0])
        self.assertFalse(validar_nombre("   ")[0])
        self.assertFalse(validar_nombre("a;b")[0])
        self.assertFalse(validar_nombre("x" * 13)[0])
        self.assertEqual(validar_puntaje("1500"), (True, 1500))
        self.assertFalse(validar_puntaje("15a")[0])
        self.assertFalse(validar_puntaje("-3")[0])
        self.assertFalse(validar_puntaje("")[0])


if __name__ == "__main__":
    unittest.main()
