#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Author: Mykolaj Konovalow
    for SPC department of NTU "KhPI"
"""

VERSION = (0, 3, 1)

import sys
import logging
import _thread
import urllib.request
import urllib.error
from traceback import format_exception
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QMenu
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QPushButton
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
    sig_update = QtCore.pyqtSignal()
    sig_clear = QtCore.pyqtSignal()
    sig_mayUpdate = QtCore.pyqtSignal()

    def __init__(self):
        super(MyWindow, self).__init__()
        uic.loadUi('ui/main.ui', self)

        # First call of resizeEvent (call when window create)
        # will initialize a 2 QPixmap buffer

        size_tip = QPushButton()
        size_tip.setStyleSheet("QPushButton{ font-weight: bold; }")
        size_tip.setFocusPolicy(QtCore.Qt.NoFocus)  # instead mess with arrows
        txt = "Размеры рабочей области.\nПо нажатию масштабирует область"
        size_tip.setToolTip(txt)

        self.msg = None
        self.statusbar.addPermanentWidget(QLabel("Рабочая область:"))
        self.statusbar.addPermanentWidget(size_tip)
        self.prims_dialog = PrimitivesListDialog()
        self.figure = Figure(size_tip, self.sig_update, self.sig_clear)

        size_tip.clicked.connect(self.figure.adjust)
        self.wipe_world.triggered.connect(self.clean)
        self.save_world.triggered.connect(self.save)
        self.save_world_as.triggered.connect(self.save_as)
        self.shut_app_down.triggered.connect(self.close)
        self.import_figure.triggered.connect(self.pre_import)
        self.export_figure.triggered.connect(self.pre_export)

        self.add_rectangle.triggered.connect(self.figure.new_figure)
        self.edit_figure.triggered.connect(self.show_prims_dialog)
        self.create_world.triggered.connect(self.figure.create_space)

        self.sig_update.connect(self.updating)
        self.sig_clear.connect(self.clearing)
        self.sig_mayUpdate.connect(self.propose_upgrade)
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
        p.setRenderHint(QPainter.HighQualityAntialiasing)
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
        if self.msg:
            self.statusbar.removeWidget(self.msg)
            self.msg = None
        if self.figure.message != "":
            self.statusbar.showMessage(self.figure.message, 4000)
            self.figure.message = ""

        canvas = QPainter(self.canvas_figure_buffer)
        mesh_canvas = QPainter(self.canvas_mesh_buffer)
        dx, dy = self.getCanvasSize()
        self.figure.redraw(canvas, dx, dy, mesh_canvas)
        self.repaint()

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
        if e.button() != QtCore.Qt.RightButton:
            return

        x = e.x() - OFFSET_X
        y = e.y() - OFFSET_Y
        canvas = self.canvas_figure.frameGeometry()
        min_x, min_y, max_x, max_y = canvas.getCoords()
        if not (min_x < x and x < max_x and min_y < y and y < max_y):
            return

        menu = QMenu(self)
        s = self
        # self.prim_n* defined in ui/main.ui
        actions = [s.prim_del, s.prim_edit, s.prim_nt, s.prim_nr, s.prim_nb,
                   s.prim_nl, s.wipe_world, s.add_rectangle]

        dx, dy = self.getCanvasSize()
        target_ind = self.figure.click_over(x, y, dx, dy)
        if target_ind != -1:
            menu.addAction(actions[0])
            menu.addAction(actions[1])
            expand = menu.addMenu("Добавить примитив")
            expand.addAction(actions[2])
            expand.addAction(actions[3])
            expand.addAction(actions[4])
            expand.addAction(actions[5])
            menu.addAction(actions[6])
        else:
            menu.addAction(actions[7])  # new rectangle
            menu.addAction(actions[6])  # delete all

        pos = self.mapToGlobal(e.pos())
        pos.setX(pos.x() + 5)
        selected_act = menu.exec_(pos)
        if selected_act:
            act_ind = actions.index(selected_act)
            if act_ind == 0:
                self.figure.del_prim(target_ind)
            elif act_ind == 1:
                self.figure.mod_prim(target_ind)
            elif act_ind > 1 and act_ind < 6:
                self.figure.expand(target_ind, act_ind-2)

    def show_prims_dialog(self):
        self.prims_dialog.show(self.figure)

    def save(self):
        self.figure.save_mesh()

    def save_as(self):
        fname = QFileDialog.getSaveFileName(self, 'Сохранить как...',
                                            '', "Text files (*.pmd)")[0]
        if fname != '':
            self.figure.save_mesh(fname)

    def shit_happens(self):
        msg = QMessageBox(QMessageBox.Critical, "Крепитесь!", '')
        msg.setText("Непоправимое произошло...\nПриложение будет закрыто.\n"
                    "Данные об ошибке записаны в errors.log")
        msg.exec_()
        sys.exit()

    def propose_upgrade(self):
        self.msg = QLabel('Доступно <a href="https://github.com/SPC-project/'
                          'Regular-Divider">обновление!</a>')
        self.msg.setOpenExternalLinks(True)
        self.statusbar.addWidget(self.msg)

    def pre_import(self):
        fname = QFileDialog.getOpenFileName(self, 'Открыть...', './samples',
                                            "Text files (*.d42do)")[0]
        if fname != '':
            self.figure.importing(fname)

    def pre_export(self):
        fname = QFileDialog.getSaveFileName(self, 'Открыть...', './samples',
                                            "Text files (*.d42do)")[0]
        if fname != '':
            self.figure.exporting(fname)


def my_excepthook(type_, value, tback):
    logging.error(''.join(format_exception(type_, value, tback)))
    sys.__excepthook__(type_, value, tback)
    window.shit_happens()


def check_updates(recall):
    """
    Get version fresh program from GitHub, compare with self and, if have
        nevest - propose to update

    First line of Changelog.txt is: v<major>.<minor>.[<revision>]\n
    """
    ch_url = 'https://raw.githubusercontent.com/SPC-project/Regular-Divider'\
        '/master/Changelog.txt'
    try:
        changelog = urllib.request.urlopen(ch_url)
    except (urllib.error.URLError, urllib.error.HTTPError,
            urllib.error.ContentTooShortError):
        return

    changelog = urllib.request.urlopen(ch_url)
    first_line = changelog.readline().decode('utf-8')[1:-1]  # del 'v' and '\n'
    version_code = first_line.split('.')
    major = int(version_code[0])
    minor = int(version_code[1])
    revision = 0
    if len(version_code) == 3:
        revision = int(version_code[2])

    if major > VERSION[0] or minor > VERSION[1] or revision > VERSION[2]:
        recall.emit()

if __name__ == '__main__':
    log_format = '[%(asctime)s]  %(message)s'
    logging.basicConfig(format=log_format, level=logging.ERROR,
                        filename='errors.log')

    app = QApplication(sys.argv)
    window = MyWindow()

    _thread.start_new_thread(check_updates, (window.sig_mayUpdate,))

    sys.excepthook = my_excepthook
    sys.exit(app.exec_())
