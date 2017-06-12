#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Author: Mykolaj Konovalow
    for CMPS department of NTU "KhPI"
    http://web.kpi.kharkov.ua/cmps/ru/kafedra-cmps/

Visualize .pmd files

Input:
    argv[1] — filename
"""

import sys
import logging
from traceback import format_exception
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtGui import QPainter, QPixmap, QColor, QPolygon, QBrush
from PyQt5.QtCore import QPoint
from PyQt5 import uic
from Sorter import read_pmd

PADDING = 10  # Space between window border and QFrame
OFFSET = 4  # QFrame's area start not at (0;0), but (4;4) because curving
CAMERA_OFFSET = 3
BLANK = QColor(0, 0, 0, 0)
COL_AIR = QColor(0, 0, 255, 127)
COL_FIG = QColor(0, 0, 0)
COL_FIG_INNNER = QColor(0, 0, 0, 64)


class Displayer(QMainWindow):
    def __init__(self, filename):
        super().__init__()
        uic.loadUi('resources/ui/displayer.ui', self)

        self.data = False
        self.buffer = False

        if filename:
            self.load_pmd(filename)

        self.shut_app_down.triggered.connect(self.close)
        self.open.triggered.connect(self.select_pmd)

        self.show()

    def select_pmd(self):
        fname = QFileDialog.getOpenFileName(self, 'Открыть...', './',
                                            "Text files (*.pmd*)")[0]
        if fname:
            self.load_pmd(fname)

    def load_pmd(self, filename):
        In = open(filename, 'r')
        elems, coords, mat = read_pmd(In)

        # Prepare data
        def describe_element(index, elem):
            A, B, C = elem
            first = (coords[A][0], coords[A][1])
            second = (coords[B][0], coords[B][1])
            third = (coords[C][0], coords[C][1])
            return (first, second, third, mat[index])

        self.data = tuple(
            describe_element(i, elem) for i, elem in enumerate(elems)
        )
        self.show_message("Загружен {}".format(filename))

        # Figure out the camera's parameters
        coords.sort(key=lambda node: (node[1], node[0]))
        max_x = max(coords, key=lambda node: node[0])[0]
        max_y = max(coords, key=lambda node: node[1])[1]
        min_x = min(coords, key=lambda node: node[0])[0]
        min_y = min(coords, key=lambda node: node[1])[1]
        print(max_x, min_x, max_y, min_y)
        dx = max_x - min_x + 2*CAMERA_OFFSET
        dy = max_y - min_y + 2*CAMERA_OFFSET
        self.world_size = max(dx, dy)
        self.start_x = min_x - CAMERA_OFFSET
        self.start_y = min_y - CAMERA_OFFSET
        print(self.world_size, self.start_x, self.start_y)

        self.display_pmd()

    def show_message(self, text):
        self.statusbar.showMessage(text, 4000)

    def shit_happens(self):
        msg = QMessageBox(QMessageBox.Critical, "Ошибка!", '')
        msg.setText("Непоправимое произошло...\n"
                    "Данные об ошибке записаны в errors.log")
        msg.exec_()

    def getCanvasSize(self):
        dx = self.geometry().width() - 2*PADDING
        dy = self.geometry().height() - self.menubar.height() - self.statusbar.height()
        return int(dx), int(dy)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.HighQualityAntialiasing)
        p.drawPixmap(self.draw_x, self.draw_y, self.buffer)

    def resizeEvent(self, event):
        dx, dy = self.getCanvasSize()
        self.canvas.resize(dx, dy)

        if not dx == dy:
            msg = "Изменение размеров... Холсты: {} {} (рекомендуются квадратные)"
            self.show_message(msg.format(dx, dy))

        self.draw_x = self.canvas.x() + OFFSET
        self.draw_y = self.canvas.y() + self.menubar.height() + OFFSET

        dx -= 2*OFFSET  # Prevent QPixmap from overlap QFrame's borders
        dy -= 2*OFFSET
        self.buffer = QPixmap(dx, dy)
        self.clearing()
        self.display_pmd()

    def clearing(self):
        self.buffer.fill(BLANK)

    def display_pmd(self):
        if not self.data:
            return
        if not self.buffer:
            return

        W, H = self.getCanvasSize()
        kx = int(W/self.world_size)
        ky = int(H/self.world_size)
        shift_x = -self.start_x
        shift_y = -self.start_y

        def scale(vertex):
            canvas_x = int(round((shift_x + vertex[0])*kx))
            canvas_y = int(round((shift_y + vertex[1])*ky))
            return (canvas_x, canvas_y)

        painter = QPainter(self.buffer)
        for A, B, C, material in self.data:
            self.draw_element(A, B, C, material, scale, painter)

        self.repaint()

    def draw_element(self, A, B, C, material, scale, painter):
        first = QPoint(*scale(A))
        second = QPoint(*scale(B))
        third = QPoint(*scale(C))

        element = QPolygon()
        element.append(first)
        element.append(second)
        element.append(third)
        element.append(first)
        if material == 1:
            painter.setPen(COL_FIG)
            painter.setBrush(QBrush(COL_FIG_INNNER))  # drawPolygon() use it
        else:
            painter.setPen(COL_AIR)
            painter.setBrush(QBrush(BLANK))
        painter.drawPolygon(element)


def my_excepthook(type_, value, tback):
    """
    Перехватывает исключения, логгирует их и позволяет уронить програму
    """
    logging.error(''.join(format_exception(type_, value, tback)))
    sys.__excepthook__(type_, value, tback)
    window.shit_happens()


if __name__ == '__main__':
    log_format = 'Displayer.py — [%(asctime)s]  %(message)s'
    logging.basicConfig(format=log_format, level=logging.ERROR,
                        filename='errors.log')
    sys.excepthook = my_excepthook

    app = QApplication(sys.argv)
    window = Displayer(sys.argv[1] if len(sys.argv) > 1 else False)
    sys.exit(app.exec_())
