import time
from math import cos, sin, radians
from threading import Condition, Lock
from random import random, randint, choice
import numpy
from PyQt5.QtCore import pyqtSignal, QThread, Qt, QTimer
from constantes import *
from colisiones import check_collision, check_collision_with_label, \
    check_click_on_label, euclidean_distance
import csv
import os


class Character:
    def __init__(self, parent, x, y, tamaño=2):
        self.parent = parent
        self._x = x
        self._y = y
        self.image = None
        self._rotation = 0
        self._tamaño = tamaño
        self._velocidad = 0
        self.i = 9
        self.atacando = False
        self._vida_maxima = 0
        self.c = 0  # bonificaciones
        self.bonificacion = 0
        self.vida_actual = self.vida_maxima
        self._experiencia = 0   # parte en 0
        self.puntaje = PUNTAJE_INICIO
        self.timer_puntaje = QTimer()
        self.timer_puntaje.timeout.connect(self.aumentar_puntaje)
        self.timer_puntaje.start(1000)
        self.timer_revision = QTimer()
        self.timer_revision.timeout.connect(self.revision)
        self.timer_revision.start(100)
        self.zona_segura = False

    @property
    def tamaño(self):
        return self._tamaño

    @tamaño.setter
    def tamaño(self, value):
        if value > 10:
            self._tamaño = 10
        else:
            self._tamaño = value

    @property
    def velocidad(self):
        self._velocidad = (2-self.tamaño/8) * 1.1 ** self.bonificacion
        return self._velocidad

    def avanzar2(self, QKeyEvent):
        if QKeyEvent.text() == "w":
            # time.sleep(0.05)  # para ajustar velocidad
            self.x -= self.velocidad*cos(radians(self.rotation))
            self.y -= self.velocidad*sin(radians(self.rotation))

        elif QKeyEvent.text() == "s":
            self.x += self.velocidad*cos(radians(self.rotation))
            self.y += self.velocidad*sin(radians(self.rotation))

    def subir_nivel(self, nuevo_nivel):
        self.experiencia = 0
        self.puntaje += 1500 + PUNTAJE_NIVEL * nuevo_nivel

    def revision(self):
        if self.parent.label_safe_zone and \
                check_collision_with_label(self, self.parent.label_safe_zone):
            self.zona_segura = True
            self.image.setVisible(False)
        else:
            self.zona_segura = False
            self.image.setVisible(True)

        for label in self.parent.puntajes_extra:
            if check_collision_with_label(self, label):
                # print("GANO 1000")
                self.puntaje += 1000
                label.setVisible(False)
        self.parent.puntajes_extra = [lab for lab in self.parent.puntajes_extra
                                      if lab.isVisible()]

        for label in self.parent.vidas_extra:
            if check_collision_with_label(self, label):
                # print("GANO VIDA")
                self.vida_actual = self.vida_maxima
                label.setVisible(False)
        self.parent.vidas_extra = [lab for lab in self.parent.vidas_extra
                                   if lab.isVisible()]

    @property
    def experiencia(self):
        return self._experiencia

    @experiencia.setter
    def experiencia(self, value):
        if value > 1000:
            self._experiencia = 1000
        else:
            self._experiencia = value

    @property
    def vida_maxima(self):
        self._vida_maxima = (self.tamaño * 20 + 100) * (1.2 ** self.c)
        return self._vida_maxima

    @property
    def diag(self):
        pixmap = self.image.pixmap()
        self._diag = (pixmap.width() ** 2 + pixmap.height() ** 2) ** 0.5
        return self._diag

    @property
    def centro(self):
        self._centro = (self.x + self.image.width() / 2,
                        self.y + self.image.height() / 2)
        return self._centro

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        if value == 360 or value == -360:
            self._rotation = 0
        else:
            self._rotation = value

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, posicion):  # colision borde izq y der
        if posicion < 30:  # 0
            self._x = 30
        elif posicion + self.image.width() > self.parent.width() - 30:
            self._x = self.parent.width() - 30 - self.image.width()
        else:
            self._x = posicion

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, posicion):  # colision borde arr y aba
        if posicion < 30:
            self._y = 30
        elif posicion + self.image.height() > self.parent.height() - 30:
            self._y = self.parent.height() - 30 - self.image.height()  # 450
        else:
            self._y = posicion

    def generar_ataque(self):
        self.daño = round(self.tamaño * self.vida_maxima / 10, 0)
        return self.daño

    def ganar_experiencia(self, tamaño_enemigo):
        ganados = 100 * max(tamaño_enemigo - self.tamaño + 3, 1)
        self.experiencia += ganados
        self.puntaje += 1000 + PUNTAJE_ENEMIGO * (tamaño_enemigo - self.tamaño)

    def aumentar_puntaje(self):
        self.puntaje += PUNTAJE_TIEMPO


class Enemy(QThread):
    id = 0

    def __init__(self, parent, x, y, tamaño=1):
        super().__init__()
        self.parent = parent
        self.trigger = parent.threads_response3
        self.victima = parent.jug_principal
        self.image = None
        self._x = x
        self._y = y
        self._rotation = randint(0, 359)
        self.tamaño = tamaño
        self.velocidad = 0
        self._rango_vision = None
        self._rango_escape = None
        self._centro = None
        self.paused = False
        self.state = Condition(Lock())
        self.atacando = False
        self.esta_escapando = False
        self.esta_acercando = False
        self._vida_maxima = 0
        self.vida_actual = self.vida_maxima
        self.id = Enemy.id
        Enemy.id += 1
        self.tiempo_inicio_ataque = 0
        self.progressbar = None
        self.bombeado = False  # True cuando muere por bomba

    @property
    def vida_maxima(self):
        self._vida_maxima = self.tamaño * 20 + 100
        return self._vida_maxima

    @property
    def diag(self):
        pixmap = self.image.pixmap()
        self._diag = (pixmap.width() ** 2 + pixmap.height() ** 2) ** 0.5
        return self._diag

    @property
    def centro(self):
        self._centro = (self.x + self.image.width() / 2,
                        self.y + self.image.height() / 2)
        return self._centro

    @property
    def rango_vision(self):
        self._rango_vision = self.tamaño * RANGO_VISION  # es por 30 normalmte
        return self._rango_vision

    @property
    def rango_escape(self):
        self._rango_escape = self.rango_vision * 1.5
        return self._rango_escape

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        if value == 360 or value == -360:
            self._rotation = 0
        else:
            self._rotation = value

    def avanzar(self):
        # time.sleep(1)  # para ajustar velocidad
        initx = self.x
        inity = self.y
        self.x -= (2-self.tamaño/8)*cos(radians(self.rotation))
        self.y -= (2-self.tamaño/8)*sin(radians(self.rotation))
        others = [en for en in self.parent.enemies if en.image is not None]
        for other in others:
            if other != self and check_collision(other, self):  # ENEM-ENEM
                self.x = initx
                self.y = inity
                # print("choque")
                if not self.esta_acercando or self.esta_escapando:
                    self.rotation = choice([0, 90, 180, 270])
                break
        self.trigger.emit(self)

    def ataque(self):
        self.atacando = True
        self.victima.atacando = True
        daño_a_enemigo = self.victima.generar_ataque()
        self.vida_actual -= daño_a_enemigo
        # time.sleep(1)
        self.victima.vida_actual -= self.generar_ataque()
        self.tiempo_inicio_ataque = time.time()

    def escape(self):  # INTELIGENCIA
        time.sleep(TIEMPO_VELOCIDAD_ENEMIGOS)
        a = numpy.array(self.victima.centro)
        b = numpy.array(self.centro)
        norma = numpy.linalg.norm(b - a)
        v = (b - a) / norma  # se normaliza
        if v[1] >= 0:
            self.rotation = - 90 - numpy.degrees(numpy.arcsin(v[0]))
        else:
            self.rotation = 90 + numpy.degrees(numpy.arcsin(v[0]))
        self.avanzar()

    def acercarse(self):
        time.sleep(TIEMPO_VELOCIDAD_ENEMIGOS)
        a = numpy.array(self.victima.centro)
        b = numpy.array(self.centro)
        norma = numpy.linalg.norm(b - a)
        v = (a - b) / norma  # se normaliza
        if v[1] >= 0:
            self.rotation = - 90 - numpy.degrees(numpy.arcsin(v[0]))
        else:
            self.rotation = 90 + numpy.degrees(numpy.arcsin(v[0]))
        self.avanzar()

    def run(self):
        while self.vida_actual > 0:
            with self.state:
                if self.paused:
                    self.state.wait()
            # time.sleep(0.1)
            if time.time() - self.tiempo_inicio_ataque >= 1:
                self.atacando = False
                self.victima.atacando = False
            # if check_collision(self, self.victima):
                # print("COLISION")
            if not self.victima.zona_segura and \
                    (euclidean_distance(self.centro,
                                        self.victima.
                                        centro) < self.rango_vision or
                     check_collision(self, self.victima)):

                if check_collision(self, self.victima) and not self.atacando:
                    # print("ACA EMPEZARIA EL ATAQUE")
                    self.ataque()
                else:
                    # INTELIGENCIA
                    if self.tamaño < self.victima.tamaño or \
                            self.esta_escapando:
                        # print("Esta escapando!!")
                        self.esta_escapando = True
                        self.escape()  # aca avanza
                    elif self.tamaño == self.victima.tamaño and \
                            not self.esta_acercando:
                        p = random()
                        if p < 0.5:
                            # print("El enemigo se acerca!!")
                            self.esta_acercando = True
                            self.acercarse()
                        else:
                            # print("Esta escapando!!")
                            self.esta_escapando = True
                            self.escape()
                    else:
                        # print("El enemigo se acerca!!")
                        self.esta_acercando = True
                        self.acercarse()
            elif euclidean_distance(self.centro,
                                    self.victima.centro) < self.rango_escape \
                    and not self.victima.zona_segura and self.esta_escapando:

                # print("DEBERIA SEGUIR ESCAPANDO")
                self.escape()
            elif euclidean_distance(self.centro,
                                    self.victima.centro) < self.rango_escape \
                    and not self.victima.zona_segura and self.esta_acercando:

                # print("DEBERIA SEGUIR ACERCANDOSE")
                self.acercarse()

            else:
                self.esta_escapando = False
                self.esta_acercando = False
                now = time.time()
                while time.time() - now <= 1:
                    time.sleep(TIEMPO_VELOCIDAD_ENEMIGOS)
                    self.avanzar()  # aca avanza
                prob = random()
                if prob < 0.25:
                    self.rotation = randint(0, 360)
                # FIN INTELIGENCIA
        if not self.bombeado:
            self.victima.ganar_experiencia(self.tamaño)
        self.victima.atacando = False  # cuando muere, deja de atacar
        self.quit()
        self.image.deleteLater()
        self.progressbar.deleteLater()
        self.image = None

    def resume(self):
        with self.state:
            self.paused = False
            self.state.notify()

    def pause(self):
        with self.state:
            self.paused = True

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, posicion):  # colision borde izq y der
        if posicion < 30:
            self._x = 30
        elif posicion + self.image.width() > self.parent.width() - 30:
            self._x = self.parent.width() - 30 - self.image.width()
        else:
            self._x = posicion

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, posicion):  # colision borde arr y aba
        if posicion < 30:
            self._y = 30
            if not self.esta_escapando and not self.esta_acercando:
                self.rotation = 0
        elif posicion + self.image.height() > self.parent.height() - 30:
            self._y = self.parent.height() - 30 - self.image.height()
            if self.x == 0:
                self.rotation = choice([90, -90])
            elif self.x == 1000 - self.image.width():
                self.rotation = choice([0, 180])
        else:
            self._y = posicion

    def generar_ataque(self):
        self.daño = round(self.tamaño * self.vida_maxima / 10, 0)
        return self.daño

    def __str__(self):
        return str(self.id)


class Bomba(QThread):
    def __init__(self, parent, x, y):
        super().__init__()
        self.parent = parent
        self.trigger = parent.threads_response4
        self.image = None
        self.label_contador = None
        self.contador = 3
        self.x = x
        self.y = y

    @property
    def centro(self):
        self._centro = (self.x + self.image.width() / 2,
                        self.y + self.image.height() / 2)
        return self._centro

    def run(self):
        while True:
            colision = False
            time.sleep(0.1)
            self.parent.enemies = [en for en in self.parent.enemies
                                   if en.image is not None]
            for enemy in self.parent.enemies:
                if check_collision(enemy, self):
                    # print("Bomba explota")
                    colision = True
                    break
            if colision:
                break
            if check_collision(self.parent.jug_principal, self):
                # print("Bomba explota")
                break
        while self.contador > -1:
            self.trigger.emit(self)
            time.sleep(1)
            self.contador -= 1
        self.label_contador.deleteLater()
        self.image.deleteLater()


def registrar_puntaje(nombre, puntaje):
    if os.path.exists("ranking.csv"):
        header = True
    else:
        header = False
    with open("ranking.csv", "a", newline="") as file:
        writer = csv.writer(file)
        if not header:
            writer.writerow(["Nombre", "Puntaje"])
        writer.writerow([nombre, str(puntaje)])


def abrir_ranking():
    with open("ranking.csv", "r") as file:
        reader = csv.DictReader(file)
        lista = sorted(reader, key=lambda x: int(x["Puntaje"]), reverse=True)
        return lista
