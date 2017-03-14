from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QDialog, QMessageBox
from src.rectangle import Rectangle
from src.triangle import Triangle
from src.primitive import NewPrimitiveDialog, AbstractPrimitive

SPACING = 5
RECT = 0  # Index of generate-rectangle tab in NewPrimitiveDialog
TRI = 1


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

        self.prim_dialog = NewPrimitiveDialog()

        self.update_status()

    def clean(self):
        self.world_size = 0
        self.start_x = 0
        self.start_y = 0
        self.shape.clear()
        self.parent_clear.emit()
        self.parent_update.emit()

    def update_status(self):
        self.status.setText("{:g}x{:g}".format(
            self.world_size, self.world_size))
        self.status.adjustSize()

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
        self.prim_dialog.grab_focus()
        self.prim_dialog.exec_()
        if self.prim_dialog.result() == 1:
            self.parent_clear.emit()
            self.adopt_primitive(*self.prim_dialog.get_data())

    def adopt_primitive(self, fig, mesh, prim_type_index, primitive_ind=-1):
        x, y, w, h = fig

        if primitive_ind == -1:
            primitive = None
            if prim_type_index == RECT:
                primitive = Rectangle(fig, mesh)
            elif prim_type_index == TRI:
                primitive = Triangle(fig, mesh)
            self.shape.append(primitive)
        else:
            self.shape[primitive_ind].modify(fig, mesh)

        not_match_x = x+w > self.world_size or x <= self.start_x
        not_match_y = y+h > self.world_size or y <= self.start_y
        if not_match_x or not_match_y:
            self.message = "Рабочая область была расширена"
            self.adjust()
        else:
            self.parent_update.emit()

    def redraw(self, canvas, canvas_width, canvas_height, mesh_canvas):
        if self.world_size == 0:
            return

        kx = int(canvas_width/self.world_size)
        ky = int(canvas_height/self.world_size)
        shift_x = -self.start_x
        shift_y = -self.start_y
        for primitive in self.shape:
            primitive.draw(canvas, mesh_canvas, shift_x, shift_y, kx, ky)

    def mod_prim(self, ind):
        dialog = NewPrimitiveDialog()
        dialog.set_data(self.shape[ind])
        dialog.grab_focus()
        dialog.exec_()
        if dialog.result() == 1:
            self.parent_clear.emit()
            fig, mesh, prim_type_index = dialog.get_data()
            self.adopt_primitive(fig, mesh, prim_type_index, ind)

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
        self.shape.sort(key=lambda prim: prim.start_x)
        self.shape.sort(key=lambda prim: prim.start_y)

        isRegular = True
        stp_x = self.shape[0].step_x
        stp_y = self.shape[0].step_y
        for prim in self.shape:
            if stp_x != prim.step_x and stp_y != prim.step_y:
                isRegular = False
                break

        if isRegular:
            self.regular_mesh_saving(filename)
        else:
            self.irregular_mesh_saving(filename)

    def regular_mesh_saving(self, filename):
        min_x = float("inf")
        min_y = float("inf")
        max_x = float("-inf")
        max_y = float("-inf")
        for prim in self.shape:
            x, y, X, Y = prim.get_box()
            if x < min_x:
                min_x = x
            if y < min_y:
                min_y = y
            if X > max_x:
                max_x = X
            if Y > max_y:
                max_y = Y

        dk = self.shape[0].step_x
        curr = 0
        frame_x, frame_y, frame_X, frame_Y = self.shape[curr].get_box()
        for j in range(int(max_y/dk)):
            for i in range(int(max_x/dk)):
                x = min_x + i*dk
                y = min_y + j*dk

    def irregular_mesh_saving(self, filename):
        '''
        Владельцем узлов на стыке двух примитивов считают правый/нижний сосед
        '''
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
        possible_dirs = [2, 3, 4, 5]
        x = self.start_x + x * self.world_size/canvas_width
        y = self.start_y + y * self.world_size/canvas_height
        for i, prim in enumerate(self.shape):
            if prim.x < x and x < prim.x + prim.width:
                if prim.y < y and y < prim.y + prim.height:
                    possible_dirs = (2, 3, 4, 5)  # see MyWindow.mousePressEvent()
                    if prim.mesh.data['type'] == 'triangle':
                        form = prim.mesh.data['form']
                        if form == 0:
                            possible_dirs = (5, 4)
                        elif form == 1:
                            possible_dirs = (4, 3)
                        elif form == 2:
                            possible_dirs = (2, 5)
                        else:
                            possible_dirs = (3, 2)
                    return i, possible_dirs

        return -1, None

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

        dialog = NewPrimitiveDialog()
        dialog.for_expanding(prim, side_code)
        dialog.grab_focus()
        dialog.exec_()

        if dialog.result() == 1:
            self.adopt_primitive(*dialog.get_data())
            new_prim = self.shape[-1]
            prim.shave_air(side_code, new_prim)
            new_prim.shave_air((side_code+2) % 4, prim)  # shave opposite side
            self.parent_clear.emit()
            self.parent_update.emit()

    def exporting(self, filename):
        if len(self.shape) == 1:
            self.send_message("Экспортировать нечего: фигура пуста")
            return

        with open(filename, 'w') as f:
            for prim in self.shape:
                prim.export_figure(f)

            f.write("# connections\n")
            for prim in self.shape:
                for side in prim.binds:
                    if side:
                        f.write("{} ".format(self.shape.index(side)))
                    else:
                        f.write("-1 ")
                f.write("\n")

        self.send_message("Фигура экспортирована в " + filename)

    def importing(self, filename):
        self.shape.clear()
        with open(filename, 'r') as f:
            still_read_primitives = True
            shift = 0
            for i, line in enumerate(f.readlines()):
                if line[0:1] == '#':
                    still_read_primitives = False
                    shift = i+1
                    continue

                if still_read_primitives:
                    data = line.split(' | ')
                    fig, mesh, prim_type_index = AbstractPrimitive.parse(data)
                    self.adopt_primitive(fig, mesh, prim_type_index)
                else:
                    data = line.split(' ')
                    for side, code in enumerate(data[:-1]):  # last is '\n'
                        code = int(code)
                        if code != -1:
                            neighbour = self.shape[code]
                            self.shape[i-shift].shave_air(side, neighbour)
        self.adjust()
        self.parent_clear.emit()
        self.parent_update.emit()

    def adjust(self):
        if len(self.shape) == 0:
            self.send_message("Нечего масштабировать: фигура пуста")
            return

        min_x = float('infinity')
        min_y = float('infinity')
        max_x = float('-infinity')
        max_y = float('-infinity')
        for prim in self.shape:
            x0, y0, x1, y1 = prim.get_box()
            if x0 < min_x:
                min_x = x0
            if y0 < min_y:
                min_y = y0
            if x1 > max_x:
                max_x = x1
            if y1 > max_y:
                max_y = y1

        self.start_x = min_x - SPACING
        self.start_y = min_y - SPACING
        max_width = max_x - min_x + 2*SPACING
        max_height = max_y - min_y + 2*SPACING
        if max_width > max_height:
            self.world_size = int(max_width)
        else:
            self.world_size = int(max_height)

        self.update_status()
        self.parent_clear.emit()
        self.parent_update.emit()