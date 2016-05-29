#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Author: Mykolaj Konovalow
    for SPC department of NTU "KhPI"
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QMenu
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QPainter, QPixmap, QColor
from figure import Figure
from figure_managing import PrimitivesListDialog

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

        # First call of resizeEvent (call when window create)
        # will initialize a 2 QPixmap buffer

        size_tip = QLabel()
        self.statusbar.addPermanentWidget(size_tip)
        self.prims_dialog = PrimitivesListDialog()

        self.edit_figure.triggered.connect(self.show_prims_dialog)
        self.update.connect(self.updating)
        self.clear.connect(self.clearing)
        self.figure = Figure(size_tip, self.update, self.clear)
        self.save_world.triggered.connect(self.figure.save_mesh)
        self.add_rectangle.triggered.connect(self.figure.new_figure)
        self.wipe_world.triggered.connect(self.clean)
        self.show()

    def clean(self):
        self.figure.clean()
        self.repaint()

    def getCanvasSize(self):
        dx = (self.geometry().width() - 4*OFFSET_X)/2
        dy = self.geometry().height() - OFFSET_Y - self.statusbar.height()
        return dx, dy

    def paintEvent(self, event):
        p = QPainter(self)
        # drawPixmap ignore action bar, need shift y-coordinate then
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
            self.figure.world_size += 5
            needRefresh = True
        if e.key() == QtCore.Qt.Key_Plus:
            self.figure.world_size -= 5
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

    def mousePressEvent(self, e):
        if e.button() == QtCore.Qt.RightButton:
            x = e.x() - OFFSET_X
            y = e.y() - OFFSET_Y
            canvas = self.canvas_figure.frameGeometry()
            min_x, min_y, max_x, max_y = canvas.getCoords()
            if min_x < x and x < max_x and min_y < y and y < max_y:
                dx, dy = self.getCanvasSize()
                ind = self.figure.click(x, y, dx, dy)
                if ind != -1:
                    menu = QMenu(self)
                    remove_it = menu.addAction("Удалить")
                    eddit_it = menu.addAction("Редактировать")
                    expand_it = menu.addMenu("Добавить примитив")
                    expand_to = ["Сверху", "Справа", "Снизу", "Слева"]
                    for txt in expand_to:
                        expand_it.addAction(txt)
                    pos = self.mapToGlobal(e.pos())
                    pos.setX(pos.x() + 5)
                    choice = menu.exec_(pos)
                    if choice == remove_it:
                        self.figure.del_prim(ind)
                    elif choice == eddit_it:
                        self.figure.mod_prim(ind)
                    elif choice is not None:
                        direction = expand_to.index(choice.text())
                        self.figure.expand(ind, direction)
                else:
                    menu = QMenu(self)
                    add = menu.addAction("Добавить примитив")
                    pos = self.mapToGlobal(e.pos())
                    pos.setX(pos.x() + 5)
                    choice = menu.exec_(pos)
                    if choice == add:
                        self.figure.new_figure()

    def show_prims_dialog(self):
        self.prims_dialog.show(self.figure)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())
