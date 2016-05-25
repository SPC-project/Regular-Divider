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
            fig, nx, ny = self.nf_dialog.get_data()
            self.adopt_new_figure(fig, nx, ny)

    def adopt_new_figure(self, fig, nodes_x, nodes_y, primitive_ind=-1):
        resized = False
        x, y, w, h = fig
        if x+w > self.world_size:
            self.world_size = x+w + SPACING
            resized = True
        if y+h > self.world_size:
            self.world_size = y+h + SPACING
            resized = True

        if primitive_ind == -1:
            r = Rectangle(fig, nodes_x, nodes_y)
            self.shape.append(r)
        else:
            self.shape[primitive_ind].modify(fig, nodes_x, nodes_y)

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
            fig, nx, ny = dialog.get_data()
            self.adopt_new_figure(fig, nx, ny, ind)

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
            fig, nx, ny = dialog.get_data()
            self.adopt_new_figure(fig, nx, ny)
            new_prim = self.shape[-1]

            if side_code == 0:
                prim.shrink_top_air()
                new_prim.shrink_bottom_air()
            elif side_code == 1:
                prim.shrink_right_air()
                new_prim.shrink_left_air()
            elif side_code == 2:
                prim.shrink_bottom_air()
                new_prim.shrink_top_air()
            elif side_code == 3:
                prim.shrink_left_air()
                new_prim.shrink_right_air()

            self.parent_clear.emit()


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

        Nleft, Nx, Nright = rectangle.nodes_x
        Ntop, Ny, Nbottom = rectangle.nodes_y
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
            Nright = Ntop
            Nbottom = Ntop
            Nleft = Ntop
            if self.watched_node != -1:
                if self.watched_node == 0:
                    Nbottom = 0
                    y -= height
                elif self.watched_node == 1:
                    Nleft = 0
                elif self.watched_node == 2:
                    Ntop = 0
                elif self.watched_node == 3:
                    Nright = 0
                    x -= width

        return (x, y, width, height), (Nleft, Nx, Nright), (Ntop, Ny, Nbottom)

    def for_expanding(self, prim, side_code):
        self.watched_node = side_code
        if side_code == 0 or side_code == 2:
            if side_code == 0:
                self.y.setValue(prim.y)
                self.air_bottom.hide()
            else:
                self.y.setValue(prim.y + prim.height)
                self.air_top.hide()
            self.y.setEnabled(False)
            self.x.setValue(prim.x)
            self.x.setSingleStep(prim.step_x)
            self.width.setValue(prim.width)
            self.width.setSingleStep(prim.step_x)
            self.Nx.setValue(prim.nodes_x[1])
            self.Nx.setEnabled(False)
            self.wath_node(self.Nx, prim.step_x)
        elif side_code == 1 or side_code == 3:
            if side_code == 1:
                self.x.setValue(prim.x + prim.width)
                self.air_right.hide()
            else:
                self.x.setValue(prim.x)
                self.air_left.hide()
            self.x.setEnabled(False)
            self.y.setValue(prim.y)
            self.y.setSingleStep(prim.step_y)
            self.height.setValue(prim.height)
            self.height.setSingleStep(prim.step_y)
            self.Ny.setValue(prim.nodes_y[1])
            self.Ny.setEnabled(False)
            self.wath_node(self.Ny, prim.step_y)

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
        Nk.setValue(int(dk/self.dezired_step)+1)  # need N+1 dot for N segments
