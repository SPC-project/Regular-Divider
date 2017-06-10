from PyQt5 import uic, QtCore
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDialog, QMessageBox
from src.rectangle import Rectangle
from src.triangle import Triangle
from src.primitive import AbstractPrimitive
from src.gui_primitive import NewPrimitiveDialog
import subprocess
import os
import sys

SPACING = 5
RECT = 0  # Index of generate-rectangle tab in NewPrimitiveDialog
TRI = 1


class Figure(QtCore.QObject):
    primitive_deletion = QtCore.pyqtSignal(int)
    primitive_modification = QtCore.pyqtSignal(int)
    COL_GRID = QColor(0, 0, 0, 24)

    def __init__(self, status, parent_update, parent_clear, parent_message):
        super().__init__()
        self.world_size = 0
        self.grid_step = 0
        self.start_x = 0
        self.start_y = 0
        self.message = ""
        self.shape = list()
        self.prim_dialog = False  # wait for NewPrimitiveDialog creation
        self.show_coordinate_grid = False

        self.status = status
        self.parent_update = parent_update
        self.parent_clear = parent_clear
        self.parent_message = parent_message
        self.primitive_deletion.connect(self.del_prim)
        self.primitive_modification.connect(self.mod_prim)

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
        self.parent_message.emit()
        self.update_status()

    def create_space(self):
        dialog = QDialog()
        uic.loadUi('resources/ui/create_space.ui', dialog)
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
            self.send_message("Рабочая область изменена")
            self.parent_clear.emit()
            self.parent_update.emit()

    def new_figure(self):
        if not self.prim_dialog:
            self.prim_dialog = NewPrimitiveDialog()

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
            self.send_message("Рабочая область была расширена")
            self.adjust()
        else:
            self.parent_update.emit()

        # Select step for coordinate grid
        step_x = min(self.shape, key=lambda prim: prim.step_x).step_x
        step_y = min(self.shape, key=lambda prim: prim.step_y).step_y
        self.grid_step = min(step_x, step_y)

    def redraw(self, canvas, canvas_width, canvas_height, mesh_canvas):
        if self.world_size == 0:
            return

        kx = int(canvas_width/self.world_size)
        ky = int(canvas_height/self.world_size)
        shift_x = -self.start_x
        shift_y = -self.start_y

        if self.show_coordinate_grid and self.grid_step > 0.000001:
            N = int(self.world_size / self.grid_step)
            dx = kx * self.grid_step
            dy = ky * self.grid_step
            edge_prim = min(self.shape, key=lambda prim: (prim.start_y, prim.start_x))
            x0 = int(round((shift_x + edge_prim.start_x)*kx)) % dx
            y0 = int(round((shift_y + edge_prim.start_y)*ky)) % dy

            start = 1 if x0 == 0 else 0
            for i in range(start, N):
                x = x0 + i*dx
                y = y0 + i*dy
                canvas.setPen(self.COL_GRID)
                canvas.drawLine(x, 0, x, canvas_height)
                canvas.drawLine(0, y, canvas_width, y)
                mesh_canvas.setPen(self.COL_GRID)
                mesh_canvas.drawLine(x, 0, x, canvas_height)
                mesh_canvas.drawLine(0, y, canvas_width, y)
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
        if len(self.shape) == 0:
            self.send_message("Фигура пуста, нечего сохранять")
            return

        self.shape.sort(key=lambda prim: (prim.start_x, prim.start_y))

        elem_num = 0
        with Output() as output:
            for prim in self.shape:
                prim.save_mesh(output)
            elem_num = output.elements_amount

        res = subprocess.run([sys.executable, "./Combiner.py", filename, str(elem_num)]).returncode
        if res == 0:
            self.send_message("Фигура сохранена в " + filename)
        else:
            self.send_message("Не удалось сохранить фигуру. Подробности в errors.log")

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
            msg.setText("Нельзя достраивать"
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
            prim.connect(side_code, new_prim)
            new_prim.connect((side_code+2) % 4, prim)  # shave opposite side
            self.parent_clear.emit()
            self.parent_update.emit()

    def exporting(self, filename):
        if len(self.shape) == 0:
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
                            self.shape[i-shift].connect(side, neighbour)
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
                min_x = int(x0)
            if y0 < min_y:
                min_y = int(y0)
            if x1 > max_x:
                max_x = int(x1)
            if y1 > max_y:
                max_y = int(y1)

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

    def set_air(self, thickness):
        for primitive in self.shape:
            for i in range(4):
                if not primitive.binds[i]:
                    primitive.mesh.set_val_at(i, thickness)
                    primitive.modify()

            self.parent_clear.emit()
        self.parent_update.emit()


class Output:
    """
    Вспомогательный класс для записи данных разбиения в промежуточные файлы
    """
    TEMP_DIR = ".temp/"
    FILENAMES = ["elements", "nodes", "elements_material", "nodes_material"]

    def __init__(self):
        self.f = {}
        self.last_index = 0
        self.elements_amount = 0

    def __enter__(self):
        if not os.path.isdir(self.TEMP_DIR):
            os.mkdir(self.TEMP_DIR)

        for tmp_name in self.FILENAMES:
            self.f[tmp_name] = open(self.TEMP_DIR + tmp_name + ".tmp", "w")  # TODO: should be "x"
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        for tmp_name in self.FILENAMES:
            self.f[tmp_name].close()

    def save_element(self, index_A, index_B, index_C, material):
        self.f[self.FILENAMES[0]].write("{} {} {}\n".format(index_A, index_B, index_C))
        self.f[self.FILENAMES[2]].write("{}\n".format(material))
        self.elements_amount += 1

    def save_node(self, x, y, material):
        self.f[self.FILENAMES[1]].write("{} {} {}\n".format(x, y, self.last_index))
        self.f[self.FILENAMES[3]].write("{}\n".format(material))
        self.last_index += 1
