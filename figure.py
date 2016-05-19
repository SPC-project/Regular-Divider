from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
from primitives import Rectangle
from mesh import Mesh


class Figure:
    def __init__(self, status, parent_update, parent_clear):
        self.status = status
        self.parent_update = parent_update
        self.parent_clear = parent_clear
        self.world_width = 0
        self.world_height = 0
        self.start_x = 0
        self.start_y = 0
        self.message = ""
        self.shape = list()
        self.mesh = Mesh()

        self.dialog = QDialog()
        uic.loadUi('ui/new_figure.ui', self.dialog)
        self.dialog.manual_air.stateChanged.connect(self.precise_air)

        self.update_status()

    def precise_air(self, value):
        p = value == 2
        self.dialog.air_left.setEnabled(p)
        self.dialog.air_right.setEnabled(p)
        self.dialog.air_bottom.setEnabled(p)

    def update_status(self):
        self.status.setText("Рабочая область: <b>{:g}x{:g}<\b>".format(
            self.world_width, self.world_height))

    def sendMessage(self, text):
        self.message = text
        self.parent_update.emit()
        self.update_status()

    def create_space(self):
        dialog = QDialog()
        uic.loadUi('ui/create_space.ui', dialog)
        dialog.width.setFocus()
        dialog.exec_()
        if dialog.result() == 1:
            self.world_width = dialog.width.value()
            self.world_height = dialog.height.value()
            self.start_x = dialog.start_x.value()
            self.start_y = dialog.start_y.value()
            self.parent_clear.emit()
            self.sendMessage("Рабочая область создана")

    def new_figure(self):
        self.dialog.x.setFocus()
        self.dialog.exec_()
        if self.dialog.result() == 1:
            self.parent_clear.emit()
            x = self.dialog.x.value()
            y = self.dialog.y.value()
            width = self.dialog.width.value()
            height = self.dialog.height.value()
            Nx = self.dialog.Nx.value()
            Ny = self.dialog.Ny.value()
            NAtop = self.dialog.air_top.value()
            NAright = self.dialog.air_right.value()
            NAbottom = self.dialog.air_bottom.value()
            NAleft = self.dialog.air_left.value()
            if not self.dialog.manual_air.isChecked():
                NAright = NAtop
                NAbottom = NAtop
                NAleft = NAtop

            self.adopt_new_figure(x, y, width, height, Nx, Ny, NAtop, NAright,
                                  NAbottom, NAleft)

    def adopt_new_figure(self, x, y, width, height, Nx, Ny, Nt, Nr, Nb, Nl):
        resized = False
        if x+width > self.world_width:
            self.world_width = x+width + 5
            resized = True
        if y+height > self.world_height:
            self.world_height = y+height + 5
            resized = True
        r = Rectangle(x, y, width, height, Nx, Ny)
        self.shape.append(r)
        self.mesh.add(r, Nx, Ny, Nt, Nr, Nb, Nl)
        if resized:
            self.sendMessage("Рабочая область была расширена")
        else:
            self.parent_update.emit()

    def redraw(self, canvas, canvas_width, canvas_height, mesh_canvas):
        if self.world_width == 0 or self.world_height == 0:
            return

        kx = canvas_width/self.world_width
        ky = canvas_height/self.world_height
        shift_x = -self.start_x
        shift_y = -self.start_y
        for primitive in self.shape:
            primitive.draw(canvas, shift_x, shift_y, kx, ky)

        self.mesh.redraw(mesh_canvas, shift_x, shift_y, kx, ky)
