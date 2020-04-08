from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (QWidget, QLabel)
from PyQt5.QtGui import QPixmap
from constantes import *
from backend import *


class Tienda(QWidget):
    def __init__(self, jug_principal):
        super().__init__()
        self.jugador = jug_principal
        self.setGeometry(400, 200, 600, 400)

        self.setWindowTitle("TIENDA")
        self.label_fondo = QLabel(self)
        self.label_fondo.setGeometry(0, 0, 600, 400)
        pmap = QPixmap("Assets/fondo_tienda.jpg").scaled(600, 400)
        self.label_fondo.setPixmap(pmap)

        self.label_puntaje = QLabel(self)
        self.label_puntaje.setGeometry(40, 160, 300, 100)
        self.label_puntaje.setStyleSheet("QLabel {font-family: Courier;"
                                         "font-size: 18px}")
        self.timer_puntaje = QTimer(self)
        self.timer_puntaje.timeout.connect(self.act_puntaje)

        self.label_movimiento = QLabel(self)
        self.label_movimiento.setGeometry(120, 60, 100, 120)
        self.label_movimiento.setStyleSheet(DISEÑO_LABEL_INVENTARIO)
        texto = QLabel("$250 Puntos", self)
        texto.setStyleSheet("QLabel {font-family: Courier}")
        texto.move(130, 160)

        self.label_ataque = QLabel(self)
        self.label_ataque.setGeometry(260, 60, 100, 120)
        self.label_ataque.setStyleSheet(DISEÑO_LABEL_INVENTARIO)
        texto = QLabel("$500 Puntos", self)
        texto.setStyleSheet("QLabel {font-family: Courier}")
        texto.move(270, 160)

        self.label_vida = QLabel(self)
        self.label_vida.setGeometry(400, 60, 100, 120)
        self.label_vida.setStyleSheet(DISEÑO_LABEL_INVENTARIO)
        texto = QLabel("$750 Puntos", self)
        texto.setStyleSheet("QLabel {font-family: Courier}")
        texto.move(410, 160)

        self.im_movimiento = QLabel(self)
        self.im_movimiento.move(135, 80)
        self.im_movimiento.setPixmap(QPixmap("Assets/"
                                             "velocidad_movimiento.jpg"))

        self.im_ataque = QLabel(self)
        self.im_ataque.move(275, 80)
        self.im_ataque.setPixmap(QPixmap("Assets/velocidad_ataque.jpg"))

        self.im_vida = QLabel(self)
        self.im_vida.move(415, 80)
        self.im_vida.setPixmap(QPixmap("Assets/vida.jpg"))

        self.labels_inventario = []
        self.poderes = [None, None, None, None, None]
        for i in range(5):
            label = QLabel(self)
            label.setGeometry(60 + i*100, 250, 80, 100)
            label.setStyleSheet(DISEÑO_LABEL_INVENTARIO)
            self.labels_inventario.append(label)

    def mouseMoveEvent(self, QMouseEvent):
        if self.arrastre1 or self.arrastre2 or self.arrastre3:
            self.temporal.show()
            self.temporal.move(QMouseEvent.x(), QMouseEvent.y())
            for inv in self.labels_inventario:
                if check_click_on_label(QMouseEvent, inv):
                    self.temporal.move(inv.x() + 5, inv.y() + 5)
                    if self.arrastre1:
                        self.poderes[self.labels_inventario.
                                     index(inv)] = "movimiento"
                    elif self.arrastre2:
                        self.poderes[self.labels_inventario.
                                     index(inv)] = "ataque"
                    elif self.arrastre3:
                        self.poderes[self.labels_inventario.
                                     index(inv)] = "vida"

                    break

    def mousePressEvent(self, QMouseEvent):
        if check_click_on_label(QMouseEvent, self.im_movimiento) and \
                self.jugador.puntaje >= 350:
            self.temporal = QLabel(self)
            self.temporal.setPixmap(self.im_movimiento.pixmap())
            self.arrastre1 = True
        else:
            self.arrastre1 = False
        if check_click_on_label(QMouseEvent, self.im_ataque) and \
                self.jugador.puntaje >= 500:
            self.temporal = QLabel(self)
            self.temporal.setPixmap(self.im_ataque.pixmap())
            self.arrastre2 = True
        else:
            self.arrastre2 = False
        if check_click_on_label(QMouseEvent, self.im_vida) and \
                self.jugador.puntaje >= 750:
            self.temporal = QLabel(self)
            self.temporal.setPixmap(self.im_vida.pixmap())
            self.arrastre3 = True
        else:
            self.arrastre3 = False

    def mouseReleaseEvent(self, QMouseEvent):
        esta = False
        if self.temporal is not None:
            for inv in self.labels_inventario:
                if check_click_on_label(QMouseEvent, inv):
                    esta = True
                    if self.arrastre1:
                        self.jugador.puntaje -= 350
                        self.arrastre1 = False
                    elif self.arrastre2:
                        self.jugador.puntaje -= 500
                        self.arrastre2 = False
                    elif self.arrastre3:
                        self.jugador.puntaje -= 750
                        self.arrastre3 = False
                    break
            if not esta:
                self.temporal.deleteLater()
        self.temporal = None

    def act_puntaje(self):
        self.label_puntaje.setText("Puntaje: " + str(self.jugador.puntaje))
        self.jugador.c = self.poderes.count("vida")
        self.jugador.bonificacion = self.poderes.count("movimiento")
