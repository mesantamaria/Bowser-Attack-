import sys
import os
import time
from random import expovariate, randint, uniform, triangular
from PyQt5.QtCore import pyqtSignal, QThread, Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QTransform, QFont
from PyQt5.QtWidgets import (QWidget, QApplication, QLabel, QLineEdit,
                             QPushButton, QProgressBar)
from backend import Character, Enemy, check_collision, \
    Bomba, check_click_on_label, registrar_puntaje, abrir_ranking, \
    euclidean_distance
from constantes import *
from tienda import Tienda


class Inicio(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setGeometry(200, 100, 1000, 600)
        self.label_fondo = QLabel(self)
        self.label_fondo.move(0, 0)
        self.label_fondo.resize(self.width(), self.height())
        pmap = QPixmap("Assets/fondo1.jpg")
        pmap = pmap.scaled(self.width(), self.height())
        self.label_fondo.setPixmap(QPixmap(pmap))

        self.label_logo = QLabel(self)
        self.label_logo.move(0, 0)
        pmap = QPixmap("Assets/logo.png")
        pmap = pmap.scaled(pmap.width()/2, pmap.height()/2)  # 400 , 779/2
        self.label_logo.setPixmap(pmap)

        self.label_titulo = QLabel("The Bowser", self)
        self.label_titulo.move(400, 250)
        font = QFont("Times", 64, QFont.Bold)
        self.label_titulo.setFont(font)
        self.label_titulo.setStyleSheet("QLabel "
                                        "{background-color : darkgreen}")

        self.label_titulo2 = QLabel("ATTACK", self)
        self.label_titulo2.move(650, 340)
        font = QFont("Times", 64, QFont.Bold)
        self.label_titulo2.setFont(font)
        self.label_titulo2.setStyleSheet(
            "QLabel {background-color : lightgreen}")

        self.boton_comenzar = QPushButton('Comenzar el juego', self)
        self.boton_comenzar.clicked.connect(self.comenzar_juego)
        self.boton_comenzar.setFont(QFont("Courier", 18, QFont.Black))
        self.boton_comenzar.setStyleSheet("QPushButton {background-color: "
                                          "orange; border-width: 4px;"
                                          "border-color: orange;"
                                          "border-style: outset}")
        self.boton_comenzar.resize(self.boton_comenzar.sizeHint())
        self.boton_comenzar.move(50, 450)

        self.boton_ranking = QPushButton('Mostrar el ranking', self)
        self.boton_ranking.clicked.connect(self.mostrar_ranking)
        self.boton_ranking.setFont(QFont("Courier", 18, QFont.Black))
        self.boton_ranking.setStyleSheet("QPushButton {background-color: "
                                         "orange; border-width: 4px;"
                                         "border-color: orange;"
                                         "border-style: outset}")
        self.boton_ranking.resize(self.boton_ranking.sizeHint())
        self.boton_ranking.move(50, 500)

        self.show()

    def comenzar_juego(self):
        self.juego = MiVentana()
        self.close()

    def mostrar_ranking(self):
        if os.path.exists("ranking.csv"):
            ranking = abrir_ranking()
            self.label_ranking = QLabel()
            self.label_ranking.setStyleSheet("QLabel {margin: 50px;"
                                             "background-color: orange;"
                                             "font-size: 24px;"
                                             "font-family: Courier;"
                                             "font-weight: bold}")
            string = "10 MEJORES PUNTAJES\n"
            for i, jugador in enumerate(ranking[:10]):
                string += str(i+1) + "- "
                string += jugador["Nombre"] + " "
                string += jugador["Puntaje"] + "\n"
            self.label_ranking.setText(string)
            self.label_ranking.setGeometry(450, 150, 500, 500)
            self.label_ranking.show()


class MiVentana(QWidget):
    threads_response1 = pyqtSignal(object)
    threads_response2 = pyqtSignal(object)
    threads_response3 = pyqtSignal(object)
    threads_response4 = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.paused = False
        self.ataque = False
        self.enemies = []
        self.nivel = 1

        self.init_GUI()

    def init_GUI(self):
        # geometria de ventana
        # Parámetros: (x_top_left, y_top_left, width, height)
        self.setGeometry(200, 100, 1000, 600)
        self.setWindowTitle('DCCell')

        self.label_borde = QLabel(self)
        self.label_borde.move(0, 0)
        self.label_borde.resize(self.width(), self.height())
        pmap = QPixmap("Assets/fondo1.jpg")
        pmap = pmap.scaled(self.width(), self.height())
        self.label_borde.setPixmap(QPixmap(pmap))

        self.label_fondo = QLabel(self)
        self.label_fondo.move(30, 30)
        self.label_fondo.resize(self.width() - 60, self.height() - 60)
        pmap = QPixmap("Assets/fondo2.jpg")
        pmap = pmap.scaled(self.width() - 60, self.height() - 60)
        self.label_fondo.setPixmap(QPixmap(pmap))
        # FIN GEOMETRIA VENTANA

        # BOTONES
        self.boton_pausa = QPushButton('PAUSA', self)
        self.boton_pausa.clicked.connect(self.pausar)
        self.boton_pausa.resize(self.boton_pausa.sizeHint())
        self.boton_pausa.move(30, 575)
        self.boton_pausa.setStyleSheet("QPushButton {background-color: "
                                       "orange; border-width: 4px;"
                                       "border-color: orange;"
                                       "border-style: outset;"
                                       "font-weight: bold;"
                                       "font-family: Courier}")

        self.boton_tienda = QPushButton('TIENDA', self)
        self.boton_tienda.clicked.connect(self.abrir_tienda)
        self.boton_tienda.resize(self.boton_tienda.sizeHint())
        self.boton_tienda.move(120, 575)
        self.boton_tienda.setStyleSheet("QPushButton {background-color: "
                                        "orange; border-width: 4px;"
                                        "border-color: orange;"
                                        "border-style: outset;"
                                        "font-weight: bold;"
                                        "font-family: Courier;}")

        self.boton_salir = QPushButton('SALIR', self)
        self.boton_salir.clicked.connect(self.salir)
        self.boton_salir.resize(self.boton_salir.sizeHint())
        self.boton_salir.move(890, 575)
        self.boton_salir.setStyleSheet("QPushButton {background-color: "
                                       "orange; border-width: 4px;"
                                       "border-color: orange;"
                                       "border-style: outset;"
                                       "font-weight: bold;"
                                       "font-family: Courier;}")
        # FIN BOTONES

        # Images Jugador Principal
        self.jug_principal = Character(self, 200, 200)
        self.jug_principal.image = QLabel(self)
        pixmap = QPixmap("Assets/bowser/bowser_02.png")
        pixmap = pixmap.scaled(22 + 7 * self.jug_principal.tamaño,
                               22 + 7 * self.jug_principal.tamaño)

        diag = (pixmap.width()**2 + pixmap.height()**2)**0.5
        self.jug_principal.image.setMinimumSize(diag, diag)
        self.jug_principal.image.setAlignment(Qt.AlignCenter)
        self.jug_principal.image.move(200, 200)

        self.jug_principal.image.setPixmap(QPixmap(pixmap))
        self.jug_principal.image.show()
        self.tienda = Tienda(self.jug_principal)

        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(250, 575, 400, 20)
        self.pbar.setStyleSheet("QProgressBar {text-align: center; "
                                "font-weight: bold}")
        self.timer_pbar = QTimer()
        self.timer_pbar.timeout.connect(self.update_pbar)
        self.timer_pbar.start(100)

        self.label_puntaje = QLabel(self)
        self.label_puntaje.setGeometry(400, 5, 250, 20)
        self.label_puntaje.setStyleSheet("QLabel {font-weight: bold;"
                                         "font-family: Courier;"
                                         "font-size: 18px}")

        self.pbar_exp = QProgressBar(self)
        self.pbar_exp.setMinimumSize(20, 400)
        self.pbar_exp.move(975, 100)
        self.pbar_exp.setOrientation(Qt.Vertical)
        self.label_nivel = QLabel("LVL\n " + str(self.nivel), self)
        self.label_nivel.move(975, 60)
        self.label_nivel.setStyleSheet("QLabel {font-size: 12px;"
                                       "font-weight: bold}")

        # self.pbar_exp.setTextDirection(QProgressBar.BottomToTop)
        # self.pbar_exp.setTextVisible(True)

        #self.pbar_exp.setInvertedAppearance(True)

        # Threads y Timers
        self.timer1 = QTimer(self)  # sprites
        self.timer1.timeout.connect(self.update_movimiento)
        self.numero = 2
        self.i = 10  # era 9
        self.timer1.start(100)

        self.timer2 = QTimer(self)  # aparicion enemigos
        self.timer2.timeout.connect(self.new_enemy)
        self.timer2.start(expovariate(1 / 10) * 1000)
        self.show()

        self.threads_response3.connect(self.update_position)
        self.threads_response4.connect(self.bomba_explota)

        self.label_safe_zone = None
        self.timer_safe_zone = QTimer(self)
        self.timer_safe_zone.timeout.connect(self.aparece_safe_zone)
        tiempo = uniform(1, 30) * 1000
        self.timer_safe_zone.start(tiempo)

        self.puntajes_extra = []
        self.timer_puntaje_extra = QTimer(self)
        self.timer_puntaje_extra.timeout.connect(self.aparece_puntaje_extra)
        self.timer_puntaje_extra.start(uniform(1, 30) * 1000)

        self.vidas_extra = []
        self.timer_vida_extra = QTimer(self)
        self.timer_vida_extra.timeout.connect(self.aparece_vida_extra)
        self.timer_vida_extra.start(uniform(1, 30) * 1000)

        self.bombas = []
        self.timer_bomba = QTimer(self)
        self.timer_bomba.timeout.connect(self.aparece_bomba)
        self.timer_bomba.start(uniform(1, 30) * 1000)

    @property
    def lambda_aparicion(self):
        self._lambda_aparicion = 1 / (12 - 2*self.nivel)
        return self._lambda_aparicion

    @property
    def a(self):
        transform = {"1": 1, "2": 1, "3": 3, "4": 5, "5": 7}
        self._a = transform[str(self.nivel)]
        return self._a

    @property
    def b(self):
        transform = {"1": 5, "2": 6, "3": 7, "4": 9, "5": 10}
        self._b = transform[str(self.nivel)]
        return self._b

    @property
    def c(self):
        transform = {"1": 1, "2": 3, "3": 5, "4": 7, "5": 9}
        self._c = transform[str(self.nivel)]
        return self._c

    def update_movimiento(self):
        indices_ataque = ["9", "10", "11", "12", "13"]
        if self.jug_principal.atacando:
            index = self.i
        else:
            index = self.numero

        pixmap = QPixmap("Assets/bowser/bowser_" + "{:0>2d}".format(index) +
                         ".png")
        pixmap = pixmap.scaled(22 + 7 * self.jug_principal.tamaño,
                               22 + 7 * self.jug_principal.tamaño)
        diag = (pixmap.width() ** 2 + pixmap.height() ** 2) ** 0.5
        self.jug_principal.image.setMinimumSize(diag, diag)
        pixmap = pixmap.transformed(QTransform().
                                    rotate(self.jug_principal.rotation))
        self.jug_principal.image.setPixmap(QPixmap(pixmap))
        self.enemies = [enem for enem in self.enemies
                        if enem.image is not None]
        for enemigo in self.enemies:
            if enemigo.atacando:
                index = self.i
            else:
                index = self.numero
            label = enemigo.image
            pixmap = QPixmap("Assets/clubba/clubba_" + "{:0>2d}".format(index)
                             + ".png")
            pixmap = pixmap.scaled(22 + 7 * enemigo.tamaño,
                                   22 + 7 * enemigo.tamaño)
            pixmap = pixmap.transformed(QTransform().
                                        rotate(enemigo.rotation))
            if label is not None:
                label.setPixmap(QPixmap(pixmap))
        self.numero += 1
        if self.numero >= 10:  # era 10
            self.numero = 2
        self.i += 1
        if self.i >= 14:
            self.i = 10  # era 9

    def new_enemy(self):
        tamaño = int(triangular(self.a, self.b, self.c))
        enemy = Enemy(self, 0, 0, tamaño)
        label = QLabel(self)
        label.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap("Assets/clubba/clubba_02.png")
        pixmap = pixmap.transformed(QTransform().
                                    rotate(enemy.rotation))
        pixmap = pixmap.scaled(22 + 7 * enemy.tamaño,
                               22 + 7 * enemy.tamaño)
        diag = (pixmap.width() ** 2 + pixmap.height() ** 2) ** 0.5

        label.setMinimumSize(diag, diag)
        label.setPixmap(QPixmap(pixmap))
        enemy.image = label
        valida = False
        while not valida:
            enemy.x = randint(0, 900)
            enemy.y = randint(0, 500)
            for enem in self.enemies:
                if enem != enemy and check_collision(enem, enemy):
                    valida = False
                    break
                else:
                    valida = True
            if len(self.enemies) == 0:
                valida = True
        label.move(enemy.x, enemy.y)
        label.show()

        progressbar = QProgressBar(self)
        progressbar.setGeometry(enemy.x, enemy.y - 5, 50, 5)
        progressbar.setValue(100)
        progressbar.setVisible(True)
        enemy.progressbar = progressbar
        enemy.start()

        self.enemies.append(enemy)
        self.timer2.stop()
        # if len(self.enemies) < 4:
        self.timer2.start(expovariate(self.lambda_aparicion) * 1000)

    def pausar(self):
        if not self.paused:
            for enemigo in self.enemies:
                enemigo.pause()
            self.timer1.stop()
            self.timer2.stop()
            self.jug_principal.timer_puntaje.stop()
            self.timer_safe_zone.stop()
            self.timer_puntaje_extra.stop()
            self.timer_vida_extra.stop()
            self.timer_bomba.stop()
            self.paused = True
        else:
            self.timer1.start(100)
            self.timer2.start(expovariate(
                1 / 10) * 1000)  # HAY QUE GUARDAR EL TIEMPO DE ANTES
            for enemigo in self.enemies:
                enemigo.resume()
            self.jug_principal.timer_puntaje.start(1000)
            if self.label_safe_zone is None:
                self.timer_safe_zone.start(uniform(1, 30)*1000)
            self.timer_puntaje_extra.start(uniform(1, 30)*1000)
            self.timer_vida_extra.start(uniform(1, 30)*1000)
            self.timer_bomba.start(uniform(1, 30) * 1000)
            self.paused = False

    def keyPressEvent(self, QKeyEvent):
        # PAUSAR
        # time.sleep(0.01)
        if QKeyEvent.modifiers() == Qt.ControlModifier and \
                QKeyEvent.key() == 83:
            self.pausar()
        elif QKeyEvent.modifiers() == Qt.ControlModifier and \
                QKeyEvent.key() == 84:
            self.abrir_tienda()
        # print('Presionaron la tecla {}'.format(QKeyEvent.text()))
        if QKeyEvent.text() == "a" and not self.paused:
            i = GRADOS_ROTACION
            pixmap = self.jug_principal.image.pixmap().transformed(QTransform()
                                                                   .rotate(-i
                                                                           ))
            self.jug_principal.rotation -= i
            self.jug_principal.image.setPixmap(QPixmap(pixmap))
        elif QKeyEvent.text() == "d" and not self.paused:
            i = GRADOS_ROTACION
            pixmap = self.jug_principal.image.pixmap().transformed(QTransform()
                                                                   .rotate(i))
            self.jug_principal.image.setPixmap(QPixmap(pixmap))
            self.jug_principal.rotation += i
        elif QKeyEvent.text() == "f" and not self.paused:
            self.ataque = True
        elif QKeyEvent.text() == "g" and not self.paused:
            self.ataque = False

        if not self.paused:
            self.jug_principal.avanzar2(QKeyEvent)
        self.jug_principal.image.move(self.jug_principal.x,
                                      self.jug_principal.y)

    def update_position(self, enemy):
        if enemy.image is not None and not self.paused:
            enemy.image.move(enemy.x, enemy.y)
            enemy.progressbar.move(enemy.x, enemy.y - 5)

    def bomba_explota(self, bomba):
        contador = bomba.label_contador
        contador.setText(str(bomba.contador))
        contador.move(bomba.x + 10, bomba.y + 10)
        contador.show()
        if bomba.contador == 0:
            pmap = QPixmap("Assets/bomba_explota.png")
            pmap = pmap.scaled(25, 25)
            bomba.image.setPixmap(pmap)
        self.enemies = [enem for enem in self.enemies
                        if enem.image is not None]
        if bomba.contador == 0:
            for enem in self.enemies:
                v1 = bomba.centro
                v2 = enem.centro
                if euclidean_distance(v1, v2) < RANGO_EXPLOSION:
                    enem.bombeado = True
                    enem.vida_actual = 0
            if euclidean_distance(self.jug_principal.centro, bomba.centro)\
                    < RANGO_EXPLOSION:
                self.jug_principal.vida_actual = 0

    def update_pbar(self):
        porcentaje = self.jug_principal.vida_actual / \
                     self.jug_principal.vida_maxima
        porcentaje = float(str(porcentaje)[:7])
        valor = porcentaje*100
        if valor <= 0:
            self.timer_pbar.stop()
            self.salir()
        self.pbar.setValue(valor)
        self.pbar.setFormat("Vida actual: " + str(int(valor)) + "%")

        self.enemies = [e for e in self.enemies if e.image is not None]
        porcentaje2 = self.jug_principal.experiencia / 1000
        valor2 = float(str(porcentaje2)[:7]) * 100
        self.pbar_exp.setValue(valor2)
        self.pbar_exp.setTextDirection(QProgressBar.BottomToTop)
        self.pbar_exp.setTextVisible(True)

        # self.pbar_exp.setFormat("Lvl " + str(self.nivel))
        if valor2 >= 50:
            self.jug_principal.tamaño = self.nivel * 2 + 1
        else:
            self.jug_principal.tamaño = self.nivel * 2
        if valor2 == 100:
            self.nivel += 1
            self.label_nivel.setText("LVL\n " + str(self.nivel))
            self.jug_principal.subir_nivel(self.nivel)

        self.label_puntaje.setText("Puntaje actual: " +
                                   str(self.jug_principal.puntaje))
        for enemy in self.enemies:
            porcentaje = enemy.vida_actual / enemy.vida_maxima
            porcentaje = float(str(porcentaje)[:7])
            valor = porcentaje * 100
            enemy.progressbar.setValue(valor)

    def aparece_safe_zone(self):
        self.label_safe_zone = QLabel(self)
        pmap = QPixmap("Assets/safe_zone.png")
        pmap = pmap.scaled(25, 25)
        self.label_safe_zone.setMinimumSize(pmap.width(), pmap.height())
        self.label_safe_zone.move(randint(40, 920), randint(40, 520))
        self.label_safe_zone.setPixmap(pmap)
        self.label_safe_zone.show()
        self.timer_safe_zone.stop()

    def aparece_puntaje_extra(self):
        self.label_puntaje_extra = QLabel(self)
        pmap = QPixmap("Assets/puntaje_extra.png")
        pmap = pmap.scaled(25, 25)
        self.label_puntaje_extra.setMinimumSize(pmap.width(), pmap.height())
        self.label_puntaje_extra.move(randint(40, 920), randint(40, 520))
        self.label_puntaje_extra.setPixmap(pmap)
        self.label_puntaje_extra.show()
        self.timer_puntaje_extra.stop()
        self.timer_puntaje_extra.start(uniform(1, 30) * 1000)
        self.puntajes_extra.append(self.label_puntaje_extra)

    def aparece_vida_extra(self):
        self.label_vida_extra = QLabel(self)
        pmap = QPixmap("Assets/vida_extra.png")
        pmap = pmap.scaled(25, 25)
        self.label_vida_extra.setMinimumSize(pmap.width(), pmap.height())
        self.label_vida_extra.move(randint(40, 920), randint(40, 520))
        self.label_vida_extra.setPixmap(pmap)
        self.label_vida_extra.show()
        self.timer_vida_extra.stop()
        self.timer_vida_extra.start(uniform(1, 30) * 1000)
        self.vidas_extra.append(self.label_vida_extra)

    def aparece_bomba(self):
        self.label_bomba = QLabel(self)
        pmap = QPixmap("Assets/bomba2.png")
        pmap = pmap.scaled(25, 25)
        self.label_bomba.setMinimumSize(pmap.width(), pmap.height())
        x = randint(40, 920)
        y = randint(40, 520)
        self.label_bomba.move(x, y)
        self.label_bomba.setPixmap(pmap)
        self.label_bomba.show()
        contador = QLabel("3", self)
        contador.setStyleSheet("QLabel {font-size: 18px; color: red;"
                               "font-width: bold}")
        new_bomb = Bomba(self, x, y)
        new_bomb.image = self.label_bomba
        new_bomb.label_contador = contador
        new_bomb.start()
        self.timer_bomba.stop()
        self.timer_bomba.start(uniform(1, 30) * 1000)
        self.bombas.append(new_bomb)

    def abrir_tienda(self):
        if not self.paused:
            self.pausar()
        self.tienda.show()
        self.tienda.timer_puntaje.start(0.1)

    def salir(self):
        if not self.paused:
            self.pausar()
        time.sleep(1)
        self.close()
        self.final = Final(self.jug_principal)
        self.final.show()


class Final(QWidget):
    def __init__(self, personaje):
        super().__init__()
        self.personaje = personaje
        self.setGeometry(200, 100, 1000, 600)
        self.label_fondo = QLabel(self)
        self.label_fondo.move(0, 0)
        self.label_fondo.resize(self.width(), self.height())
        pmap = QPixmap("Assets/fondo1.jpg")
        pmap = pmap.scaled(self.width(), self.height())
        self.label_fondo.setPixmap(QPixmap(pmap))

        self.cuadrado = QLabel(self)
        self.cuadrado.setGeometry(200, 150, 600, 300)
        self.cuadrado.setStyleSheet("QLabel {background-color: orange}")

        self.puntos = QLabel("Has obtenido " + str(self.personaje.puntaje) +
                             " puntos.", self)
        self.puntos.move(250, 230)
        self.puntos.setStyleSheet("QLabel {font-size: 24px; "
                                  "font-family: Courier;"
                                  "font-width: bold}")
        self.ingresa = QLabel("Ingresa tu nombre: ", self)
        self.ingresa.move(250, 330)
        self.ingresa.setStyleSheet("QLabel {font-size: 24px; "
                                   "font-family: Courier;"
                                   "font-width: bold}")

        self.nombre = QLineEdit(self)
        self.nombre.setGeometry(550, 330, 200, 30)
        self.nombre.setStyleSheet("QLineEdit {background-color: black;"
                                  "color: white; font-size: 20px;"
                                  "font-family: Courier}")
        self.nombre.returnPressed.connect(self.guardar_nombre)

    def guardar_nombre(self):
        registrar_puntaje(self.nombre.text(), self.personaje.puntaje)
        self.close()
        self.inicio = Inicio()


if __name__ == '__main__':
    def hook(type, value, traceback):
        print(type)
        print(traceback)


    sys.__excepthook__ = hook
    app = QApplication(sys.argv)
    menu = Inicio()
    sys.exit(app.exec_())
