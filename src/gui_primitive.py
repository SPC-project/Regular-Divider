from PyQt5.QtWidgets import QDialog, QMessageBox, QWidget
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5 import uic

from src.primitive import Mesh
import abc


class NewPrimitiveDialog(QDialog):
    def __init__(self):
        super(NewPrimitiveDialog, self).__init__()
        uic.loadUi('ui/new_primitive.ui', self)

        self.tabWidget.clear()  # Очистим пустые страницы
        self.Rectangle_widget = NewRectangleWidget()
        self.Triangle_widget = NewTriangleWidget()
        self.tabWidget.addTab(self.Rectangle_widget, "Прямоугольник")
        self.tabWidget.addTab(self.Triangle_widget, "Треугольник")

        self.accepted.connect(self.validate)

        self.tabWidget.currentChanged.connect(self.grab_focus)

    def grab_focus(self):
        self.tabWidget.currentWidget().x.setFocus()
        self.tabWidget.currentWidget().x.selectAll()

    def get_data(self):
        fig = None
        mesh = None
        curr_tab_index = self.tabWidget.currentIndex()
        if curr_tab_index == 0:
            fig, mesh = self.Rectangle_widget.get_data()
        elif curr_tab_index == 1:
            fig, mesh = self.Triangle_widget.get_data()

        return fig, mesh, curr_tab_index

    def set_data(self, primitive):
        if primitive.mesh.data['type'] == 'rectangle':
            self.tabWidget.setCurrentIndex(0)
            self.tabWidget.setTabEnabled(1, False)  # no need when redacted
            self.Rectangle_widget.set_data(primitive)
        else:
            self.tabWidget.setCurrentIndex(1)
            self.tabWidget.setTabEnabled(0, False)
            self.Triangle_widget.set_data(primitive)

    def validate(self):
        curr = self.tabWidget.currentWidget()
        if curr.height.value() == 0 or curr.width.value() == 0:
            msg = QMessageBox(QMessageBox.Critical, "Неверное значение!",
                              'Ширина и высота не могут быть равны 0')
            msg.exec_()
            self.done(0)

    def for_expanding(self, prim, side_code):
        self.Rectangle_widget.for_expanding(prim, side_code)
        self.Triangle_widget.for_expanding(prim, side_code)


class AbstractNewWidget(QWidget):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        QWidget.__init__(self)
        self.connection_side = -1

    def set_data(self, primitive):
        self.basic_set_data(primitive)
        self.specific_set_data(primitive)

    def basic_set_data(self, primitive):
        self.x.setValue(primitive.x)
        self.y.setValue(primitive.y)
        self.width.setValue(primitive.width)
        self.height.setValue(primitive.height)

        Ntop = primitive.mesh.NAT
        Nright = primitive.mesh.NAR
        Nbottom = primitive.mesh.NAB
        Nleft = primitive.mesh.NAL
        Nx = primitive.mesh.NFX
        Ny = primitive.mesh.NFY
        air = (Ntop, Nright, Nbottom, Nleft)
        self.Nx.setValue(Nx+1)  # convert back from blocks to nodes
        self.Ny.setValue(Ny+1)

        dlg = [self.air_top, self.air_right, self.air_bottom, self.air_left]
        for i in range(4):
            dlg[i].setValue(air[i])
            if primitive.binds[i]:
                dlg[i].hide()

    @abc.abstractmethod
    def specific_set_data(primitive):
        pass

    def get_data(self):
        x = self.x.value()
        y = self.y.value()
        width = self.width.value()
        height = self.height.value()

        if self.connection_side == 0:
            y -= height
        elif self.connection_side == 3:
            x -= width

        Nx = self.Nx.value() - 1  # '-1': proceed in blocks, not nodes
        Ny = self.Ny.value() - 1
        Ntop = self.air_top.value()  # no '-1' because 1 node belong to figure
        Nright = self.air_right.value()
        Nbottom = self.air_bottom.value()
        Nleft = self.air_left.value()

        mesh = [Ntop, Nright, Nbottom, Nleft, Nx, Ny]
        box, mesh, data = self.specific_get_data(x, y, width, height, mesh)
        return box, Mesh(mesh, data)

    @abc.abstractmethod
    def specific_get_data():
        pass

    def for_expanding(self, prim, side_code):
        """ Расширяем фигуру, пристраивая idxkxbxe со стороны side_code к prim
        side_code:
            0 - вверх
            1 - справа
            2 - низ
            3 - слева
        """
        self.connection_side = side_code
        self.prepare_air_for_expanding(prim, side_code)
        self.adjust_spinboxes_for_expanding(prim, side_code)

    @abc.abstractmethod
    def prepare_air_for_expanding(self, prim, side_code):
        pass

    def adjust_spinboxes_for_expanding(self, prim, side_code):
        pos = [self.x, self.y]
        dim = [self.width, self.height]
        fig = [self.Nx, self.Ny]
        prim_pos = [prim.x, prim.y]
        fixed_pos = [prim.y, prim.x + prim.width, prim.y + prim.height, prim.x]
        prim_dim = [prim.width, prim.height]
        prim_stp = [prim.step_x, prim.step_y]
        prim_bounds = [(prim.x, prim.x + prim.width),
                       (prim.y, prim.y + prim.height)]
        nodes = [prim.mesh.NFX, prim.mesh.NFY]  # mesh[4] is x

        free_axis = side_code % 2  # ось, по которой можно двигать примитив
        pos[free_axis].setValue(prim_pos[free_axis])
        pos[free_axis].setSingleStep(prim_stp[free_axis])
        pos[not free_axis].setValue(fixed_pos[side_code])
        pos[not free_axis].setEnabled(False)

        dim[free_axis].setValue(prim_dim[free_axis])
        dim[free_axis].setSingleStep(prim_stp[free_axis])  # help with scale
        dim[not free_axis].setValue(prim_stp[not free_axis])
        dim[not free_axis].setSingleStep(prim_stp[not free_axis])

        fig[free_axis].setValue(nodes[free_axis] + 1)  # +1 - go back to nodes
        fig[free_axis].setEnabled(False)
        self.wath_node(fig[free_axis], prim_stp[free_axis])
        con_min, con_max = prim_bounds[free_axis]
        self.wath_connection(pos[free_axis], con_min, con_max, free_axis == 1)

    def wath_node(self, nodes, dk):
        self.dezired_step = dk
        if nodes == self.Nx:
            self.width.valueChanged.connect(self.update_wathed_nodes)
        else:
            self.height.valueChanged.connect(self.update_wathed_nodes)

    def update_wathed_nodes(self, dk):
        if self.connection_side % 2 == 0:
            Nk = self.Nx
        else:
            Nk = self.Ny
        Nk.setValue(int(round(dk/self.dezired_step)) + 1)

    def wath_connection(self, connected_side_coor, min_, max_, isVert):
        connected_side_coor.setMaximum(max_)
        self.allowed_min = min_
        if isVert:
            connected_side_coor.setMinimum(min_ - self.height.value())
            self.height.valueChanged.connect(self.update_wathed_connection)
        else:
            connected_side_coor.setMinimum(min_ - self.width.value())
            self.width.valueChanged.connect(self.update_wathed_connection)

    def update_wathed_connection(self, length):
        if self.connection_side % 2 == 1:
            coor = self.y
        else:
            coor = self.x
        coor.setMinimum(self.allowed_min - length)


class NewRectangleWidget(AbstractNewWidget):
    """
    Важно: пользователь вводит количество узлов, но программе работать удобнее
    с "квадратами" (по диагонали которого впоследствии образуется два элемента)
    Так что при переходе туда-обратно придется прибавлять\отнимать единицу
    """
    def __init__(self):
        super(NewRectangleWidget, self).__init__()
        uic.loadUi('ui/new_rectangle.ui', self)
        self.manual_air.stateChanged.connect(self.upd_air_spinboxes)

    def upd_air_spinboxes(self, value):
        isEnabled = value == 2
        self.air_left.setEnabled(isEnabled)
        self.air_right.setEnabled(isEnabled)
        self.air_bottom.setEnabled(isEnabled)

    def specific_set_data(self, primitive):
        different = primitive.mesh.NAL != primitive.mesh.NAR
        different = different or primitive.mesh.NAT != primitive.mesh.NAB
        different = different or primitive.mesh.NAL != primitive.mesh.NAT

        if different:
            self.manual_air.setChecked(True)

    def specific_get_data(self, x, y, width, height, mesh):
        if not self.manual_air.isChecked():  # use same air for all edges
            if self.connection_side == 2:
                hold = mesh[3]
            else:
                hold = mesh[0]
            for i in range(0, 4):
                mesh[i] = hold
        if self.connection_side != -1:
            mesh[(self.connection_side+2) % 4] = 0

        other_data = {'type': 'rectangle'}
        return (x, y, width, height), mesh, other_data

    def prepare_air_for_expanding(self, prim, side_code):
        air = [self.air_top, self.air_right, self.air_bottom, self.air_left]

        to_prim = (side_code+2) % 4  # сторона, с которой находится prim
        air[to_prim].hide()

        if side_code == 2:  # air_top was default, but now it disabled
            self.air_left.setEnabled(True)


class NewTriangleWidget(AbstractNewWidget):
    def __init__(self):
        super(NewTriangleWidget, self).__init__()
        uic.loadUi('ui/new_triangle.ui', self)

        # Order for creating comboBox's items is significant
        self.comboBox.addItem(QIcon(QPixmap("ui/ld_triangle.png")), "0")
        self.comboBox.addItem(QIcon(QPixmap("ui/rd_triangle.png")), "1")
        self.comboBox.addItem(QIcon(QPixmap("ui/lu_triangle.png")), "2")
        self.comboBox.addItem(QIcon(QPixmap("ui/ru_triangle.png")), "3")
        self.comboBox.currentIndexChanged.connect(self.select_type)

    def select_type(self, index):
        boxes = [self.air_top, self.air_right, self.air_bottom, self.air_left]
        states = [False, False, True, True]
        index = int(self.comboBox.itemText(index))
        if index == 1:
            states = [False, True, True, False]
        if index == 2:
            states = [True, False, False, True]
        if index == 3:
            states = [True, True, False, False]

        for i in range(0, 4):
            boxes[i].setEnabled(states[i])
            if not states[i]:
                boxes[i].setValue(0)

        if self.connection_side != -1:
            connected_side = (self.connection_side + 2) % 4
            boxes[connected_side].setEnabled(False)

    def specific_set_data(self, triangle):
        self.comboBox.setCurrentIndex(triangle.mesh.data['form'])

    def specific_get_data(self, x, y, width, height, mesh):
        form = int(self.comboBox.itemText(self.comboBox.currentIndex()))
        other_data = {'type': 'triangle', 'form': form}
        return (x, y, width, height), mesh, other_data

    def prepare_air_for_expanding(self, triangle, side_code):
        if side_code < 2:  # use upper-left triangle when expand from top or left
            self.select_type(0)
        else:
            self.select_type(3)

        if side_code == 0:
            # Index shift after removing => bigger first
            self.comboBox.removeItem(3)
            self.comboBox.removeItem(2)
        if side_code == 1:
            self.comboBox.removeItem(3)
            self.comboBox.removeItem(1)
        if side_code == 2:
            self.comboBox.removeItem(1)
            self.comboBox.removeItem(0)
        if side_code == 3:
            self.comboBox.removeItem(2)
            self.comboBox.removeItem(0)
