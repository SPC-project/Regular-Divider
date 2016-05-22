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

    def adopt_new_figure(self, fig, nodes_x, nodes_y):
        resized = False
        x, y, w, h = fig
        if x+w > self.world_size:
            self.world_size = x+w + SPACING
            resized = True
        if y+h > self.world_size:
            self.world_size = y+h + SPACING
            resized = True
        r = Rectangle(fig, nodes_x, nodes_y)
        self.shape.append(r)

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

    def mod_prim(self, id):
        print(id)

    def del_prim(self, id):
        del self.shape[id]
        self.parent_clear.emit()
        self.parent_update.emit()

    def save_mesh(self):
        self.shape[0].save()
        self.send_message("Фигура сохранена")


class NewFigureDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        uic.loadUi('ui/new_figure.ui', self)
        self.manual_air.stateChanged.connect(self.upd_air_spinboxes)

    def upd_air_spinboxes(self, value):
        isEnabled = value == 2
        self.air_left.setEnabled(isEnabled)
        self.air_right.setEnabled(isEnabled)
        self.air_bottom.setEnabled(isEnabled)

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

        return (x, y, width, height), (Nleft, Nx, Nright), (Ntop, Ny, Nbottom)
