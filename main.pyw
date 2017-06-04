#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Author: Mykolaj Konovalow
    for CMPS department of NTU "KhPI"
    http://web.kpi.kharkov.ua/cmps/ru/kafedra-cmps/
"""

import sys
import logging
import _thread
import subprocess
import urllib.request
import urllib.error
from traceback import format_exception
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QMenu, QDialog
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QPushButton
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QPainter, QPixmap, QColor
from src.figure import Figure

VERSION = (0, 4, 1)

BLANK = QColor(0, 0, 0, 0)
OFFSET = 4  # QFrame's area start not at (0;0), but (4;4) because curving
RIGHT_BUTTON = 2
PADDING = 10


class MyWindow(QMainWindow):
    """
    Interface
    """
    sig_update = QtCore.pyqtSignal()
    sig_clear = QtCore.pyqtSignal()
    sig_message = QtCore.pyqtSignal()
    sig_mayUpdate = QtCore.pyqtSignal()

    def __init__(self):
        super(MyWindow, self).__init__()
        uic.loadUi('resources/ui/main.ui', self)

        # First call of resizeEvent (call when window create)
        # will initialize a 2 QPixmap buffer

        size_tip = QPushButton()
        size_tip.setStyleSheet("QPushButton{ font-weight: bold; }")
        size_tip.setFocusPolicy(QtCore.Qt.NoFocus)  # instead mess with arrows
        txt = "Размерность рабочей области.\nПо нажатию масштабируется чтобы вместить всё"
        size_tip.setToolTip(txt)

        self.msg = None
        self.statusbar.addPermanentWidget(QLabel("Рабочая область:"))
        self.statusbar.addPermanentWidget(size_tip)
        self.figure = Figure(size_tip, self.sig_update, self.sig_clear, self.sig_message)

        size_tip.clicked.connect(self.figure.adjust)
        self.wipe_world.triggered.connect(self.clean)
        self.save_world.triggered.connect(self.save)
        self.save_world_as.triggered.connect(self.save_as)
        self.shut_app_down.triggered.connect(self.close)
        self.import_figure.triggered.connect(self.pre_import)
        self.export_figure.triggered.connect(self.pre_export)
        self.sort_pmd.triggered.connect(self.do_sort)
        self.set_air.triggered.connect(self.do_set_air)

        self.add_primitive.triggered.connect(self.figure.new_figure)
        self.create_world.triggered.connect(self.figure.create_space)

        self.sig_update.connect(self.updating)
        self.sig_clear.connect(self.clearing)
        self.sig_message.connect(self.messaging)
        self.sig_mayUpdate.connect(self.propose_upgrade)
        self.show()

    def clean(self):
        self.figure.clean()
        self.repaint()

    def getCanvasSize(self):
        dx = (self.geometry().width() - 3*PADDING) / 2
        dy = self.geometry().height() - self.menubar.height() \
            - self.statusbar.height()
        return int(dx), int(dy)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.HighQualityAntialiasing)
        # drawPixmap ignore action bar, need shift y-coordinate then
        p.drawPixmap(self.draw_fig_x, self.draw_y, self.canvas_figure_buffer)
        p.drawPixmap(self.draw_mesh_x, self.draw_y, self.canvas_mesh_buffer)

    def resizeEvent(self, event):
        dx, dy = self.getCanvasSize()
        self.canvas_figure.resize(dx, dy)
        self.canvas_mesh.resize(dx, dy)
        self.canvas_mesh.move(PADDING + dx + PADDING, 0)

        if not (dx == dy and dx == 420):
            msg = "Изменение размеров... Холсты: " + str(dx) + "x" + str(dy)
            self.figure.message = msg + " (рекомендуются квадратные)"

        self.draw_fig_x = self.canvas_figure.x() + OFFSET
        self.draw_mesh_x = self.canvas_mesh.x() + OFFSET
        self.draw_y = self.canvas_figure.y() + self.menubar.height() + OFFSET

        dx -= 2*OFFSET  # Prevent QPixmap from overlap QFrame's borders
        dy -= 2*OFFSET
        self.canvas_mesh_buffer = QPixmap(dx, dy)
        self.canvas_figure_buffer = QPixmap(dx, dy)
        self.clearing()
        self.updating()

    def messaging(self):
        if self.msg:
            self.statusbar.removeWidget(self.msg)
            self.msg = None
        if self.figure.message != "":
            self.statusbar.showMessage(self.figure.message, 4000)
            self.figure.message = ""

    def updating(self):
        canvas = QPainter(self.canvas_figure_buffer)
        mesh_canvas = QPainter(self.canvas_mesh_buffer)
        canvas.setRenderHint(QPainter.HighQualityAntialiasing)
        mesh_canvas.setRenderHint(QPainter.HighQualityAntialiasing)
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

        x = e.x() - self.canvas_figure.x()
        y = e.y() - self.menubar.height()
        canvas = self.canvas_figure.frameGeometry()
        min_x, min_y, max_x, max_y = canvas.getCoords()
        if not (min_x < x and x < max_x and min_y < y and y < max_y):
            return

        menu = QMenu(self)
        s = self
        # self.prim_n* defined in ui/main.ui
        actions = [s.prim_del, s.prim_edit, s.prim_nt, s.prim_nr, s.prim_nb,
                   s.prim_nl, s.wipe_world, s.add_primitive]

        dx, dy = self.getCanvasSize()
        target_ind, possible_dirs = self.figure.click_over(x, y, dx, dy)
        if target_ind != -1:
            menu.addAction(actions[0])
            menu.addAction(actions[1])
            expand = menu.addMenu("Добавить примитив")
            for elem in possible_dirs:
                expand.addAction(actions[elem])
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

    def save(self):
        self.figure.save_mesh()

    def save_as(self):
        fname = QFileDialog.getSaveFileName(self, 'Сохранить как...',
                                            '', "Text files (*.pmd)")[0]
        if fname != '':
            self.figure.save_mesh(fname)

    def shit_happens(self):
        msg = QMessageBox(QMessageBox.Critical, "Ошибка!", '')
        msg.setText("Непоправимое произошло...\n"
                    "Данные об ошибке записаны в errors.log")
        msg.exec_()

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
        fname = QFileDialog.getSaveFileName(self, 'Сохранить в...', './samples',
                                            "Text files (*.d42do)")[0]
        if fname != '':
            self.figure.exporting(fname)

    def do_sort(self):
        dialog = SplitPMDDialog()
        dialog.exec_()
        if dialog.result() == 1:
            filename = dialog.pmd_filepath.text()
            divide = dialog.do_split.isChecked()

            if filename == "":
                msg = QMessageBox(QMessageBox.Critical, "Ошибка!", '')
                msg.setText("Файл для сортировки не задан")
                msg.exec_()
                return

            res = subprocess.run([sys.executable, "./Sorter.py", filename, str(divide)]).returncode
            if res == 0:
                self.msg = QLabel('Файл отсортирован успешно')
                self.statusbar.addWidget(self.msg)
            else:
                self.msg = QLabel("Не удалось отсортировать файл. Подробности в errors.log")
                self.statusbar.addWidget(self.msg)

    def do_set_air(self):
        dialog = QDialog()
        uic.loadUi('resources/ui/set_air.ui', dialog)
        dialog.exec_()
        if dialog.result() == 1:
            thickness = dialog.thickness.value()
            self.figure.set_air(thickness)


class SplitPMDDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('resources/ui/sort_pmd.ui', self)

        self.pmd_select_file.clicked.connect(self.open_select_file_dialogue)

    def open_select_file_dialogue(self):
        fname = QFileDialog.getOpenFileName(self, 'Открыть...', '.',
                                            "Text files (*.pmd)")[0]
        self.pmd_filepath.setText(fname)


def my_excepthook(type_, value, tback):
    """
    Перехватывает исключения, логгирует их и позволяет уронить программу
    """
    logging.error(''.join(format_exception(type_, value, tback)))
    sys.__excepthook__(type_, value, tback)
    window.shit_happens()


def check_updates(recall):
    """
    Get version fresh program from GitHub, compare with self and, if have
        newest - propose to update

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
