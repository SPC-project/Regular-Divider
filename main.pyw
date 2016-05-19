#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Author: Mykolaj Konovalow
    for SPC department of NTU "KhPI"
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QPainter, QPixmap, QColor
from figure import Figure

BLANK = QColor(0, 0, 0, 0)
OFFSET_X = 10
OFFSET_Y = 30
RIGHT_BUTTON = 2


class MyWindow(QMainWindow):
    """
    Interface
    """
    update = QtCore.pyqtSignal()
    clear = QtCore.pyqtSignal()

    def __init__(self):
        super(MyWindow, self).__init__()
        uic.loadUi('ui/main.ui', self)

        # In resizeEvent will initialize a 2 QPixmap buffer

        size_tip = QLabel()
        self.statusbar.addPermanentWidget(size_tip)

        self.figure = Figure(size_tip, self.update, self.clear)

        self.create_world.triggered.connect(self.figure.create_space)
        self.central_rectangle.triggered.connect(self.figure.new_figure)
        self.update.connect(self.updating)
        self.clear.connect(self.clearing)
        self.show()

    def getCanvasSize(self):
        dx = (self.geometry().width() - 4*OFFSET_X)/2
        dy = self.geometry().height() - OFFSET_Y - self.statusbar.height()
        return dx, dy

    def paintEvent(self, event):
        p = QPainter(self)
        # drawPixmap ignore action bar, need shift y-coordinate
        p.drawPixmap(OFFSET_X, OFFSET_Y, self.canvas_figure_buffer)
        p.drawPixmap(self.canvas_mesh.x(), OFFSET_Y, self.canvas_mesh_buffer)

    def resizeEvent(self, event):
        dx, dy = self.getCanvasSize()
        self.canvas_figure.resize(dx, dy)
        # Can't move onto action bar - no OFFSET_Y used then
        self.canvas_figure.move(OFFSET_X, 0)
        self.canvas_mesh.resize(dx, dy)
        self.canvas_mesh.move(3*OFFSET_X+dx, 0)

        self.canvas_mesh_buffer = QPixmap(dx, dy)
        self.canvas_figure_buffer = QPixmap(dx, dy)
        self.clearing()
        self.updating()

    def updating(self):
        if self.figure.message != "":
            self.statusbar.showMessage(self.figure.message)
            self.figure.message = ""

        canvas = QPainter(self.canvas_figure_buffer)
        mesh_canvas = QPainter(self.canvas_mesh_buffer)
        dx, dy = self.getCanvasSize()
        self.figure.redraw(canvas, dx, dy, mesh_canvas)

    def clearing(self):
        self.canvas_figure_buffer.fill(BLANK)
        self.canvas_mesh_buffer.fill(BLANK)

    def keyPressEvent(self, e):
        needRefresh = False
        if e.key() == QtCore.Qt.Key_Minus:
            self.figure.world_width += 5
            self.figure.world_height += 5
            needRefresh = True
        if e.key() == QtCore.Qt.Key_Plus:
            self.figure.world_width -= 5
            self.figure.world_height -= 5
            needRefresh = True
        if e.key() == QtCore.Qt.Key_Left:
            self.figure.start_x -= 5
            needRefresh = True
        if e.key() == QtCore.Qt.Key_Right:
            self.figure.start_x += 5
            needRefresh = True
        if e.key() == QtCore.Qt.Key_Up:
            self.figure.start_y -= 5
            needRefresh = True
        if e.key() == QtCore.Qt.Key_Down:
            self.figure.start_y += 5
            needRefresh = True

        if needRefresh:
            self.figure.update_status()
            self.clearing()
            self.updating()
            self.repaint()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())
