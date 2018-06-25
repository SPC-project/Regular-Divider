#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Author: Mykolaj Konovalow
    for CMPS department of NTU "KhPI"
    http://web.kpi.kharkov.ua/cmps/ru/kafedra-cmps/
"""

import sys
import math
import logging
from traceback import format_exception
import _thread
import urllib.request
import urllib.error
import re

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QMenu, QDialog
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QPushButton, QActionGroup
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QPainter, QPixmap, QColor, QDesktopServices
from src.figure import Figure

VERSION = (0, 4, 2)

BLANK = QColor(0, 0, 0, 0)
OFFSET = 4  # QFrame's area start not at (0;0), but (4;4) because curving (might be specific for Kubuntu theme I'm using)
RIGHT_BUTTON = 2
PADDING = 10
SIZE_TIP_EXPLENATION = "Размерность рабочей области.\nПо нажатию масштабируется чтобы вместить фигуру целиком"


class MyWindow(QMainWindow):
    """
    Interface
    """
    sig_update = QtCore.pyqtSignal()
    sig_clear = QtCore.pyqtSignal()
    sig_message = QtCore.pyqtSignal()
    sig_mayUpdate = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        uic.loadUi('resources/ui/main.ui', self)

        # Setup statusbar
        size_tip = QPushButton()
        size_tip.setStyleSheet("QPushButton{ font-weight: bold; }")
        size_tip.setFocusPolicy(QtCore.Qt.NoFocus)
        size_tip.setToolTip(SIZE_TIP_EXPLENATION)
        self.statusbar.addPermanentWidget(QLabel("Рабочая область:"))
        self.statusbar.addPermanentWidget(size_tip)

        # Other setup
        self.msg = None
        self.figure = Figure(size_tip, self.sig_update, self.sig_clear, self.sig_message)
        self.figure.show_coordinates = self.showCoordinates_flag.isChecked()

        # Qt
        self.setMouseTracking(True)
        size_tip.clicked.connect(self.figure.adjust)
        self.wipe_world.triggered.connect(self.clean)
        self.save_world.triggered.connect(self.save)
        self.save_world_as.triggered.connect(self.save_as)
        self.open_pmd.triggered.connect(self.do_open)
        self.shut_app_down.triggered.connect(self.close)
        self.import_figure.triggered.connect(self.pre_import)
        self.export_figure.triggered.connect(self.pre_export)
        self.set_air.triggered.connect(self.do_set_air)
        self.add_primitive.triggered.connect(self.figure.new_primitive)
        self.create_world.triggered.connect(self.figure.create_space)
        self.showCoordinates_flag.triggered.connect(self.switch_grid)
        self.showIndexes_flag.triggered.connect(self.indexes_displaying1)
        self.showBorderIndexes_flag.triggered.connect(self.indexes_displaying2)
        self.open_wiki.triggered.connect(self.go_wiki)
        self.check_for_updates.triggered.connect(self.initUpdateManager)

        self.sig_update.connect(self.updating)
        self.sig_clear.connect(self.clearing)
        self.sig_message.connect(self.messaging)
        self.sig_mayUpdate.connect(self.propose_upgrade)

        # Create 'showIndexes_flag' radiobuttons option
        display_indexes = QActionGroup(self)
        display_indexes.addAction(self.showIndexes_flag)
        display_indexes.addAction(self.showBorderIndexes_flag)

        # First call of resizeEvent (call when window create)
        # will initialize a 2 QPixmap buffer
        self.show()

    def clean(self):
        self.figure.clean()
        self.repaint()

    def save(self):
        self.figure.save_mesh(sortElements=self.sortElements_flag.isChecked(), splitPMD=self.splitPMD_flag.isChecked())

    def save_as(self):
        fname = QFileDialog.getSaveFileName(self, 'Сохранить как...',
                                            '', "Text files (*.pmd)")[0]
        if fname != '':
            sortElements = self.sortElements_flag.isChecked()
            splitPMD = self.splitPMD_flag.isChecked()
            self.figure.save_mesh(fname, sortElements, splitPMD)

    def do_open(self):
        fname = QFileDialog.getOpenFileName(self, 'Открыть...',
                                            'temp.pmd', "Text files (*.pmd*)")[0]
        if fname != '':
            self.figure.displayer.load_pmd(fname)
            self.figure.use_displayer = True
            self.clearing()
            self.updating()

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

    def do_set_air(self):
        dialog = QDialog()
        uic.loadUi('resources/ui/set_air.ui', dialog)
        dialog.exec_()
        if dialog.result() == 1:
            thickness = dialog.thickness.value()
            self.figure.set_air(thickness)

    def switch_grid(self, state):
        self.figure.show_coordinates = state
        self.clearing()
        self.updating()

    def indexes_displaying1(self):
        if not self.figure.use_displayer:
            self.figure.message = "Сохраните файл чтобы отобразить нумерацию фактического разбиения"
            self.messaging()

        self.figure.displayer.index_option = 1
        self.clearing()
        self.updating()

    def indexes_displaying2(self):
        if not self.figure.use_displayer:
            self.figure.message = "Сохраните файл чтобы отобразить нумерацию фактического разбиения"
            self.messaging()

        self.figure.displayer.index_option = 2
        self.clearing()
        self.updating()

    def go_wiki(self):
        QDesktopServices.openUrl(QtCore.QUrl("https://github.com/SPC-project/Regular-Divider/wiki"))
        self.figure.message = "Перенаправляем на Wiki программы"
        self.messaging()

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
            self.messaging()

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

    def clearing(self):
        self.canvas_figure_buffer.fill(BLANK)
        self.canvas_mesh_buffer.fill(BLANK)

    def updating(self):
        canvas = QPainter(self.canvas_figure_buffer)
        mesh_canvas = QPainter(self.canvas_mesh_buffer)
        canvas.setRenderHint(QPainter.HighQualityAntialiasing)
        mesh_canvas.setRenderHint(QPainter.HighQualityAntialiasing)
        dx, dy = self.getCanvasSize()
        self.figure.redraw(canvas, dx, dy, mesh_canvas)
        self.repaint()

    def keyPressEvent(self, e):
        needRefresh = False
        movement = self.figure.world_size/5
        if movement < 1:
            movement = 1

        if e.key() == QtCore.Qt.Key_Minus:
            self.figure.world_size += int(movement)
            needRefresh = True
        if e.key() == QtCore.Qt.Key_Plus:
            self.figure.world_size -= int(movement)
            needRefresh = True
        if e.key() == QtCore.Qt.Key_Left:
            self.figure.start_x -= int(movement)
            needRefresh = True
        if e.key() == QtCore.Qt.Key_Right:
            self.figure.start_x += int(movement)
            needRefresh = True
        if e.key() == QtCore.Qt.Key_Up:
            self.figure.start_y -= int(movement)
            needRefresh = True
        if e.key() == QtCore.Qt.Key_Down:
            self.figure.start_y += int(movement)
            needRefresh = True

        if needRefresh:
            self.figure.update_status()
            self.clearing()
            self.updating()
            self.repaint()

    def mousePressEvent(self, e):
        if e.button() != QtCore.Qt.RightButton:
            if self.calculateElementNumberOnClick.isChecked():
                self.processClickOnMesh(e)
            else:
                return

        x = e.x() - self.canvas_figure.x()
        y = e.y() - self.menubar.height()
        canvas = self.canvas_figure.frameGeometry()
        min_x, min_y, max_x, max_y = canvas.getCoords()
        if not (min_x < x and x < max_x and min_y < y and y < max_y):
            return

        menu = QMenu(self)
        s = self
        # self.prim_* defined in ui/main.ui
        actions = [s.prim_del, s.prim_edit, s.prim_nt, s.prim_nr, s.prim_nb,
                   s.prim_nl, s.wipe_world, s.add_primitive]

        dx, dy = self.getCanvasSize()
        target_ind, possible_dirs = self.figure.click_over(x, y, dx, dy)
        if target_ind != -1:
            menu.addAction(actions[0])
            menu.addAction(actions[1])
            if sum(possible_dirs) != 0:
                expand = menu.addMenu("Добавить примитив")
                for i in range(4):
                    if possible_dirs[i]:
                        expand.addAction(actions[i+2])
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

    def mouseMoveEvent(self, event):
        if len(self.figure.shape) == 0:
            return
        if self.calculateElementNumberOnClick.isChecked():
            return

        self.processClickOnMesh(event)

    def processClickOnMesh(self, event):
        if not self.figure.use_displayer:
            self.figure.message = 'Индекс элемента рассчитывается только на .PMD файле (сохраните разбиение сначала)'
            self.messaging()
            return

        x = event.x() - self.canvas_mesh.x()
        y = event.y() - self.canvas_mesh.y() - self.menubar.height()
        canvas_width = (self.geometry().width() - 3*PADDING) / 2
        canvas_height = self.geometry().height() - self.menubar.height() - self.statusbar.height()
        kx = self.figure.world_size/canvas_width
        ky = self.figure.world_size/canvas_height

        inWorld_x = x*kx+self.figure.start_x
        inWorld_y = y*ky+self.figure.start_y

        def calc_distance(x, y, index):
            distance = math.sqrt((x-inWorld_x)**2 + (y-inWorld_y)**2)
            return (distance, index)
        elems_centers = self.figure.displayer.elems_centers
        elems = self.figure.displayer.elems
        distances = [calc_distance(x, y, index) for x, y, index in elems_centers]

        sorted_distances = min(distances, key=lambda node: node[0])
        if sorted_distances[0] > self.figure.displayer.between_nodes:
            return
        elemet_under = sorted_distances[1]

        node1 = elems[elemet_under][0] + 1  # '+1' because displayed indexing starts from '1' and actual – from '0'
        node2 = elems[elemet_under][1] + 1
        node3 = elems[elemet_under][2] + 1
        material = self.figure.displayer.data[elemet_under][3]
        self.figure.message = "Индекс элемента под курсором: {} | Узлы: {} {} {} | Материал: {}".format(elemet_under+1, node1, node2, node3, material)
        self.messaging()

    def shit_happens(self):
        msg = QMessageBox(QMessageBox.Critical, "Ошибка!", '')
        msg.setText("Непоправимое произошло...\n"
                    "Данные об ошибке записаны в errors.log")
        msg.exec_()

    def propose_upgrade(self):
        self.msg = QLabel('Доступно <a href="https://github.com/SPC-project/Regular-Divider">обновление</a>!')
        # msg.setOpenExternalLinks(True)
        self.msg.linkActivated.connect(self.initUpdateManager)
        self.statusbar.addWidget(self.msg)

    def initUpdateManager(self):
        self.statusbar.removeWidget(self.msg)  # Remove label with the link
        self.msg = None

        manager = UpdateManager()
        manager.exec_()


def my_excepthook(type_, value, tback):
    """
    Перехватывает исключения, логгирует их и позволяет уронить программу
    """
    logging.error(''.join(format_exception(type_, value, tback)))
    sys.__excepthook__(type_, value, tback)
    window.shit_happens()


class UpdateManager(QDialog):
    RD_CHANGELOG_URL = 'https://raw.githubusercontent.com/SPC-project/Regular-Divider/master/Changelog.txt'
    header = re.compile(r'v\d+\.\d+(\.\d+)?')  # vX.Y[.Z]
    date = re.compile(r'\[\d\d\d\d-\d\d-\d\d\]')  # [YYYY-MM-DD]
    section_name = re.compile(r'### .*:')

    def __init__(self):
        super(UpdateManager, self).__init__()
        uic.loadUi('resources/ui/update_manager.ui', self)

        self.text.setReadOnly(True)
        self.button_accept.clicked.connect(self.updating)
        self.button_decline.clicked.connect(self.close)

        self.get_changelog()

    def get_changelog(self):
        try:
            changelog = urllib.request.urlopen(self.RD_CHANGELOG_URL)
        except urllib.error.URLError as error:
            self.show_title("Ошибка обновления")
            self.show_line("URL error: {}".format(error.reason))
        except urllib.error.HTTPError as error:
            self.show_title("Ошибка обновления")
            self.show_line("HTTP error {}:".format(error.code, error.reason))

        for line in changelog.readlines():
            line = line.decode('utf-8')
            if self.header.match(line):
                major, minor, revision = self.get_version(line[1:-1])  # delete 'v' and '\n'
                if major == VERSION[0] and minor == VERSION[1] and revision == VERSION[2]:
                    break

                self.show_title(line)
            elif self.date.match(line):
                self.show_date(line)
            elif self.section_name.match(line):
                self.show_section_name(line)
            else:
                self.show_line(line)

        self.text.scrollToAnchor("Start")

    def show_title(self, text):
        self.text.insertHtml("<h2 align='center'>{}</h2><br>".format(text))

    def show_date(self, text):
        self.text.setAlignment(QtCore.Qt.AlignRight)
        self.text.insertPlainText("{}".format(text))

    def show_section_name(self, text):
        self.text.insertHtml("<b>{}</b><br>".format(text[3:]))

    def show_line(self, text):
        self.text.setAlignment(QtCore.Qt.AlignLeft)
        self.text.insertPlainText("{}".format(text))

    @staticmethod
    def get_version(line):
        version_code = line.split('.')
        major = int(version_code[0])
        minor = int(version_code[1])
        revision = 0
        if len(version_code) == 3:
            revision = int(version_code[2])

        return major, minor, revision

    @staticmethod
    def check_updates(recall):
        """
        Get version of the newest program from GitHub and compare with current version

        First line of Changelog.txt is: v<major>.<minor>.[<revision>]\n
        """
        ch_url = UpdateManager.RD_CHANGELOG_URL
        try:
            changelog = urllib.request.urlopen(ch_url)
        except (urllib.error.URLError, urllib.error.HTTPError,
                urllib.error.ContentTooShortError):
            return

        changelog = urllib.request.urlopen(ch_url)
        first_line = changelog.readline().decode('utf-8')[1:-1]  # del 'v' and '\n'
        major, minor, revision = UpdateManager.get_version(first_line)
        if major > VERSION[0] or minor > VERSION[1] or revision > VERSION[2]:
            recall.emit()

    def updating(self):
        pass


if __name__ == '__main__':
    log_format = '[%(asctime)s]  %(message)s'
    logging.basicConfig(format=log_format, level=logging.ERROR,
                        filename='errors.log')

    app = QApplication(sys.argv)
    window = MyWindow()

    _thread.start_new_thread(UpdateManager.check_updates, (window.sig_mayUpdate,))

    sys.excepthook = my_excepthook
    sys.exit(app.exec_())
