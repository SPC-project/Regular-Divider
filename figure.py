from PyQt5.QtWidgets import QDialog
from PyQt5 import uic, QtCore
from primitives import Rectangle

SPACING = 5


class Figure(QtCore.QObject):
    primitive_deletion = QtCore.pyqtSignal(int)
    primitive_modification = QtCore.pyqtSignal(int)

    def __init__(self, status, parent_update, parent_clear):
        super(Figure, self).__init__()
        self.status = status
        self.parent_update = parent_update
        self.parent_clear = parent_clear
        self.world_size = 0
        self.start_x = 0
        self.start_y = 0
        self.message = ""
        self.shape = list()

        self.primitive_deletion.connect(self.del_prim)
        self.primitive_modification.connect(self.mod_prim)

        self.nf_dialog = NewFigureDialog()

        self.update_status()

    def clean(self):
        self.world_size = 0
        self.start_x = 0
        self.start_y = 0
        self.shape = list()
        self.parent_clear.emit()
        self.parent_update.emit()

    def update_status(self):
        self.status.setText("Рабочая область: <b>{:g}x{:g}<\b>".format(
            self.world_size, self.world_size))

    def send_message(self, text):
        self.message = text
        self.parent_update.emit()
        self.update_status()

    def create_space(self):
        dialog = QDialog()
        uic.loadUi('ui/create_space.ui', dialog)
        dialog.size.setFocus()
        dialog.start_x.setValue(self.start_x)
        dialog.start_y.setValue(self.start_y)
        dialog.size.setValue(self.world_size)
        dialog.exec_()
        if dialog.result() == 1:
            self.world_size = dialog.size.value()
            self.start_x = dialog.start_x.value()
            self.start_y = dialog.start_y.value()
            self.parent_clear.emit()
            self.send_message("Рабочая область создана")

    def new_figure(self):
        self.nf_dialog.x.setFocus()
        self.nf_dialog.exec_()
        if self.nf_dialog.result() == 1:
            self.parent_clear.emit()
            self.adopt_new_figure(*self.nf_dialog.get_data())

    def adopt_new_figure(self, fig, mesh, primitive_ind=-1):
        resized = False
        x, y, w, h = fig
        if x+w > self.world_size:
            self.world_size = x+w + SPACING
            resized = True
        if y+h > self.world_size:
            self.world_size = y+h + SPACING
            resized = True

        if primitive_ind == -1:
            r = Rectangle(fig, mesh)
            self.shape.append(r)
        else:
            self.shape[primitive_ind].modify(fig, mesh)

        if resized:
            self.send_message("Рабочая область была расширена")
        else:
            self.parent_update.emit()

    def redraw(self, canvas, canvas_width, canvas_height, mesh_canvas):
        if self.world_size == 0:
            return

        kx = canvas_width/self.world_size
        ky = canvas_height/self.world_size
        shift_x = -self.start_x
        shift_y = -self.start_y
        for primitive in self.shape:
            primitive.draw(canvas, mesh_canvas, shift_x, shift_y, kx, ky)

    def mod_prim(self, ind):
        dialog = NewFigureDialog()
        dialog.set_data(self.shape[ind])
        dialog.x.setFocus()
        dialog.exec_()
        if dialog.result() == 1:
            self.parent_clear.emit()
            self.adopt_new_figure(*dialog.get_data())

    def del_prim(self, id):
        del self.shape[id]
        self.parent_clear.emit()
        self.parent_update.emit()

    def save_mesh(self):
        self.shape[0].save()
        self.send_message("Фигура сохранена")

    def click(self, x, y, canvas_width, canvas_height):
        x = self.start_x + x * self.world_size/canvas_width
        y = self.start_y + y * self.world_size/canvas_height
        ind = -1
        for prim in self.shape:
            ind += 1
            if prim.x < x and x < prim.x + prim.width:
                if prim.y < y and y < prim.y + prim.height:
                    return ind

        return -1

    def expand(self, ind, side_code):
        prim = self.shape[ind]
        dialog = NewFigureDialog()
        dialog.for_expanding(prim, side_code)

        dialog.x.setFocus()
        dialog.exec_()
        if dialog.result() == 1:
            prim.shave_air(side_code)
            self.adopt_new_figure(*dialog.get_data())
            new_prim = self.shape[-1]
            new_prim.shave_air((side_code+2) % 4)  # shave opposite side


class NewFigureDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        uic.loadUi('ui/new_figure.ui', self)
        self.manual_air.stateChanged.connect(self.upd_air_spinboxes)
        self.watched_node = -1

    def upd_air_spinboxes(self, value):
        isEnabled = value == 2
        self.air_left.setEnabled(isEnabled)
        self.air_right.setEnabled(isEnabled)
        self.air_bottom.setEnabled(isEnabled)

    def set_data(self, rectangle):
        self.x.setValue(rectangle.x)
        self.y.setValue(rectangle.y)
        self.width.setValue(rectangle.width)
        self.height.setValue(rectangle.height)

        Nleft, Ntop, Nright, Nbottom, Nx, Ny = rectangle.mesh
        self.air_left.setValue(Nleft)
        self.Nx.setValue(Nx)
        self.air_right.setValue(Nright)
        self.air_top.setValue(Ntop)
        self.Ny.setValue(Ny)
        self.air_bottom.setValue(Nbottom)
        if Nleft != Nright or Ntop != Nbottom or Nleft != Ntop:
            self.manual_air.setChecked(True)

    def get_data(self):
        x = self.x.value()
        y = self.y.value()
        width = self.width.value()
        height = self.height.value()
        Nx = self.Nx.value()
        Ny = self.Ny.value()
        Ntop = self.air_top.value()
        Nright = self.air_right.value()
        Nbottom = self.air_bottom.value()
        Nleft = self.air_left.value()
        if not self.manual_air.isChecked():
            if self.watched_node == 2:
                hold = Nleft
            else:
                hold = Ntop
            Ntop = hold
            Nright = hold
            Nbottom = hold
            Nleft = hold

        mesh = [Ntop, Nright, Nbottom, Nleft, Nx, Ny]
        if self.watched_node != -1:
            mesh[(self.watched_node+2) % 4] = 0

        if self.watched_node == 0:
            y -= height
        elif self.watched_node == 3:
            x -= width

        return (x, y, width, height), mesh,

    def for_expanding(self, prim, side_code):
        self.watched_node = side_code

        pos = [self.x, self.y]
        dim = [self.width, self.height]
        air = [self.air_top, self.air_right, self.air_bottom, self.air_left]
        fig = [self.Nx, self.Ny]
        prim_pos = [prim.x, prim.y]
        oppos_pos = [prim.y, prim.x + prim.width, prim.y + prim.height, prim.y]
        prim_dim = [prim.width, prim.height]
        prim_stp = [prim.step_x, prim.step_y]

        myPos = side_code % 2
        opposite_side = (side_code+2) % 4

        pos[not myPos].setValue(oppos_pos[side_code])
        pos[not myPos].setEnabled(False)
        air[opposite_side].hide()
        pos[myPos].setValue(prim_pos[myPos])
        pos[myPos].setSingleStep(prim_stp[myPos])
        dim[myPos].setValue(prim_dim[myPos])
        dim[myPos].setSingleStep(prim_stp[myPos])
        dim[not myPos].setValue(prim_stp[not myPos])  # helpful to keep scale
        fig[myPos].setValue(prim.mesh[myPos + 4])  # x - 4, y - 5
        fig[myPos].setEnabled(False)
        self.wath_node(fig[myPos], prim_stp[myPos])

        if side_code == 2:  # air_top was default, but now it disabled
            self.air_left.setEnabled(True)

    def wath_node(self, nodes, dk):
        self.dezired_step = dk
        if nodes == self.Nx:
            self.width.valueChanged.connect(self.update_wathed_nodes)
        else:
            self.height.valueChanged.connect(self.update_wathed_nodes)

    def update_wathed_nodes(self, dk):
        if self.watched_node % 2 == 0:
            Nk = self.Nx
        else:
            Nk = self.Ny
        Nk.setValue(int(dk/self.dezired_step))
