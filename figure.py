from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QDialog, QMessageBox
from rectangle import Rectangle, NewRectangleDialog

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

        self.nf_dialog = NewRectangleDialog()

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
        dialog = NewRectangleDialog()
        dialog.set_data(self.shape[ind])
        dialog.x.setFocus()
        dialog.exec_()
        if dialog.result() == 1:
            self.parent_clear.emit()
            fig, mesh = dialog.get_data()
            self.adopt_new_figure(fig, mesh, ind)

    def del_prim(self, ind):
        to_del = self.shape[ind]
        for prim in self.shape:
            for i in range(4):
                if prim.binds[i] == to_del:
                    prim.binds[i] = None
                    continue

        del self.shape[ind]
        self.parent_clear.emit()
        self.parent_update.emit()

    def save_mesh(self, filename="temp.pmd"):
        '''
        Владельцем узлов на стыке двух примитивов считают правый/нижний сосед
        '''
        self.shape.sort(key=lambda prim: prim.start_x)
        self.shape.sort(key=lambda prim: prim.start_y)
        node_index = 0

        f = open(filename, 'w')
        f.write("[settings]\n")
        f.write("n_nodes=")
        pNumNodes = f.tell()
        f.write("     \n")  # to secure our text from overwriting
        f.write("n_elements=")
        pNumElements = f.tell()
        f.write("     \n")  # to secure our text from overwriting
        f.write("n_forces=0\n")
        f.write("n_contacts=0\n")

        sewing_nodes = list()
        material = list()

        f.write("[inds]\n")
        for prim in self.shape:
            node_index = prim.save_indexes(f, node_index)
        for prim in self.shape:
            node_index = prim.deal_with_horizontal_contact_regions(f, node_index, sewing_nodes, material)
            node_index = prim.deal_with_vertical_contact_regions(f, node_index, sewing_nodes, material)

        f.write("[coor]\n")
        for prim in self.shape:
            prim.save_coor(f)

        unique_sewing_nodes = set(sewing_nodes)
        sewing_nodes = list(unique_sewing_nodes)
        sewing_nodes.sort(key=lambda node: node[0])
        for node in sewing_nodes:
            f.write("{} {}\n".format(node[1], node[2]))

        f.write("[contact]\n")
        f.write("[force]\n")
        f.write("[material]\n")
        for prim in self.shape:
            prim.save_material(f)
        for node_mat in material:
            f.write("{}\n".format(node_mat))
        f.write("[material for elements]\n")
        for prim in self.shape:
            prim.save_material_of_element(f)

        nElements = 0
        for prim in self.shape:
            nElements += prim.element_count_w*prim.element_count_h*2
        f.seek(pNumElements)
        f.write("{}".format(nElements))
        f.seek(pNumNodes)
        f.write("{}".format(node_index))
        f.close()

        self.send_message("Фигура сохранена")

    def click_over(self, x, y, canvas_width, canvas_height):
        x = self.start_x + x * self.world_size/canvas_width
        y = self.start_y + y * self.world_size/canvas_height
        for i, prim in enumerate(self.shape):
            if prim.x < x and x < prim.x + prim.width:
                if prim.y < y and y < prim.y + prim.height:
                    return i

        return -1

    def expand(self, ind, side_code):
        prim = self.shape[ind]
        alreadyExpand = prim.binds[side_code]
        if alreadyExpand:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Пока нельзя достраивать"
                        " два примитива с одной стороны")
            msg.exec_()
            return

        dialog = NewRectangleDialog()
        dialog.for_expanding(prim, side_code)
        dialog.x.setFocus()
        dialog.exec_()

        if dialog.result() == 1:
            self.adopt_new_figure(*dialog.get_data())
            new_prim = self.shape[-1]
            prim.shave_air(side_code, new_prim)
            new_prim.shave_air((side_code+2) % 4, prim)  # shave opposite side
            self.parent_clear.emit()
            self.parent_update.emit()
