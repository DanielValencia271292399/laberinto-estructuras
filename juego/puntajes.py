"""
Tabla de mejores puntajes guardada en un ARBOL BINARIO DE BUSQUEDA (BST).

  - Clave del arbol: el puntaje (entero).
  - Valor: un objeto Registro con los datos de la partida.
  - Ranking (mayor a menor): recorrido inorden inverso.
  - Se guarda en un archivo de texto en PREORDEN: al volver a cargar e
    insertar en ese orden, el arbol queda con exactamente la misma forma.
"""

import os
from datetime import datetime

from estructuras.arbol_bst import ArbolBST
from estructuras.lista_doble import ListaDoble

SEPARADOR = ";"
LARGO_MAXIMO_NOMBRE = 12


class Registro:
    """Datos de una partida ganada."""

    def __init__(self, nombre, puntaje, dificultad, pasos, fecha=None):
        """
        Crea un registro.
        Recibe: nombre (str), puntaje (int), dificultad (str), pasos (int) y
                fecha (str "AAAA-MM-DD HH:MM"; si no se da, se usa la actual).
        Devuelve: nada.
        """
        self.nombre = nombre
        self.puntaje = int(puntaje)
        self.dificultad = dificultad
        self.pasos = int(pasos)
        self.fecha = fecha or datetime.now().strftime("%Y-%m-%d %H:%M")

    def a_linea(self):
        """Devuelve el registro como una linea de texto para el archivo."""
        return SEPARADOR.join([self.nombre, str(self.puntaje), self.dificultad,
                               str(self.pasos), self.fecha])

    @staticmethod
    def desde_linea(linea):
        """
        Crea un Registro a partir de una linea del archivo.
        Recibe: linea (str).
        Devuelve: Registro, o None si la linea esta danada.
        """
        partes = linea.strip().split(SEPARADOR)
        if len(partes) != 5:
            return None
        try:
            return Registro(partes[0], int(partes[1]), partes[2], int(partes[3]), partes[4])
        except ValueError:
            return None

    def __eq__(self, otro):
        """Dos registros son iguales si todos sus campos coinciden."""
        return (isinstance(otro, Registro) and self.nombre == otro.nombre
                and self.puntaje == otro.puntaje and self.dificultad == otro.dificultad
                and self.pasos == otro.pasos and self.fecha == otro.fecha)

    def __str__(self):
        return self.nombre + " - " + str(self.puntaje) + " pts (" + self.dificultad + ")"


def validar_nombre(texto):
    """
    Valida el nombre del jugador.
    Recibe: texto escrito por el usuario.
    Devuelve: (True, nombre_limpio) si es valido, o (False, mensaje_error).
    Reglas: de 1 a 12 caracteres; solo letras, numeros, espacios, '-' o '_'.
    """
    if texto is None:
        return False, "Escribe un nombre."
    limpio = texto.strip()
    if len(limpio) == 0:
        return False, "El nombre no puede estar vacío."
    if len(limpio) > LARGO_MAXIMO_NOMBRE:
        return False, "Máximo " + str(LARGO_MAXIMO_NOMBRE) + " caracteres."
    for caracter in limpio:
        if not (caracter.isalnum() or caracter in " -_"):
            return False, "Carácter no permitido: '" + caracter + "'"
    return True, limpio


def validar_puntaje(texto):
    """
    Valida un puntaje escrito por el usuario (para buscar en el arbol).
    Recibe: texto.
    Devuelve: (True, entero) o (False, mensaje_error).
    """
    limpio = (texto or "").strip()
    if not limpio.isdigit():
        return False, "Escribe solo números enteros positivos."
    if len(limpio) > 6:
        return False, "Número demasiado grande."
    return True, int(limpio)


class TablaPuntajes:
    """Administra los puntajes con un ArbolBST y los guarda en archivo."""

    def __init__(self, ruta_archivo="puntajes.txt"):
        """
        Crea la tabla y carga el archivo si existe.
        Recibe: ruta_archivo (str); None = no usar archivo (pruebas).
        Devuelve: nada.
        """
        self.ruta_archivo = ruta_archivo
        self.arbol = ArbolBST()
        self.cargar()

    def cargar(self):
        """
        Lee el archivo e inserta cada registro en el arbol. Las lineas
        danadas se ignoran (el juego no se cierra por un archivo malo).
        Devuelve: cantidad de registros cargados.
        """
        self.arbol = ArbolBST()
        if not self.ruta_archivo or not os.path.exists(self.ruta_archivo):
            return 0
        try:
            with open(self.ruta_archivo, "r", encoding="utf-8") as archivo:
                for linea in archivo:
                    registro = Registro.desde_linea(linea)
                    if registro is not None:
                        self.arbol.insertar(registro.puntaje, registro)
        except OSError:
            pass
        return self.arbol.tamano()

    def guardar(self):
        """
        Escribe el arbol en el archivo en PREORDEN (conserva su forma).
        Devuelve: True si pudo guardar, False si hubo error de disco.
        """
        if not self.ruta_archivo:
            return True
        try:
            with open(self.ruta_archivo, "w", encoding="utf-8") as archivo:
                for _, registro in self.arbol.preorden():
                    archivo.write(registro.a_linea() + "\n")
            return True
        except OSError:
            return False

    def agregar(self, registro):
        """
        Inserta un registro en el arbol y guarda.  O(h).
        Recibe: Registro.  Devuelve: la posicion en el ranking (1 = mejor).
        """
        self.arbol.insertar(registro.puntaje, registro)
        self.guardar()
        return self.posicion_de(registro)

    def eliminar(self, registro):
        """
        Elimina un registro especifico.  O(h).
        Recibe: Registro.  Devuelve: True si lo elimino.
        """
        eliminado = self.arbol.eliminar(registro.puntaje, registro)
        if eliminado:
            self.guardar()
        return eliminado

    def buscar(self, puntaje):
        """
        Busca un registro con ese puntaje exacto.  O(h).
        Devuelve: Registro o None.
        """
        return self.arbol.buscar(puntaje)

    def ranking(self, cantidad=10):
        """
        Mejores puntajes de mayor a menor (inorden inverso).
        Recibe: cantidad maxima.
        Devuelve: ListaDoble de Registro.  O(n).
        """
        resultado = ListaDoble()
        for _, registro in self.arbol.inorden_inverso():
            if resultado.tamano() >= cantidad:
                break
            resultado.insertar_final(registro)
        return resultado

    def posicion_de(self, registro):
        """
        Lugar del registro en el ranking (1 = mejor), o -1.  O(n).
        """
        posicion = 1
        for _, otro in self.arbol.inorden_inverso():
            if otro is registro:
                return posicion
            posicion += 1
        return -1

    def recorrido(self, tipo):
        """
        Devuelve el recorrido pedido del arbol (para mostrarlo en pantalla).
        Recibe: tipo = "inorden", "preorden" o "posorden".
        Devuelve: ListaDoble de Registro.
        """
        if tipo == "preorden":
            pares = self.arbol.preorden()
        elif tipo == "posorden":
            pares = self.arbol.posorden()
        else:
            pares = self.arbol.inorden()
        resultado = ListaDoble()
        for _, registro in pares:
            resultado.insertar_final(registro)
        return resultado
