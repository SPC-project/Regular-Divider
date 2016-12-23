from PyQt5.QtWidgets import QWidget
from PyQt5 import uic


class Mesh:
    """ Auxiliary abstraction for finite-elemental grid """
    def __init__(self, air, other=None):
        """
            NAT, NAR, NAB, NAL: [count of] Nodes Air at Top/Right/Bottom/Left
            NFX, NFY: [count of] Nodes Figure Width/Height
        """
        self.NAT, self.NAR, self.NAB, self.NAL, self.NFX, self.NFY = air
        self.data = other
        if not other:
            self.data = {type: "undefined"}

    def set_val_at(self, index, value):
        holder = [self.NAT, self.NAR, self.NAB, self.NAL, self.NFX, self.NFY]
        holder[index] = value


class NewRectangleWidget(QWidget):
    """
    Важно: пользователь вводит количество узлов, но программе работать удобнее
    с "квадратами" (по диагонали которого впоследствии образуется два элемента)
    Так что при переходе туда-обратно придется прибавлять\отнимать единицу
    """
    def __init__(self):
        QWidget.__init__(self)
        uic.loadUi('ui/new_rectangle.ui', self)
        self.manual_air.stateChanged.connect(self.upd_air_spinboxes)
        self.connection_side = -1

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

        Ntop, Nright, Nbottom, Nleft, Nx, Ny = rectangle.mesh
        air = (Ntop, Nright, Nbottom, Nleft)
        self.Nx.setValue(Nx+1)  # convert back from blocks to nodes
        self.Ny.setValue(Ny+1)

        dlg = [self.air_top, self.air_right, self.air_bottom, self.air_left]
        for i in range(4):
            dlg[i].setValue(air[i])
            if rectangle.binds[i]:
                dlg[i].hide()

        if Nleft != Nright or Ntop != Nbottom or Nleft != Ntop:
            self.manual_air.setChecked(True)

    def get_data(self):
        x = self.x.value()
        y = self.y.value()
        width = self.width.value()
        height = self.height.value()
        Nx = self.Nx.value() - 1  # '-1': proceed in blocks, not nodes
        Ny = self.Ny.value() - 1
        Ntop = self.air_top.value()  # no '-1' because 1 node belong to figure
        Nright = self.air_right.value()
        Nbottom = self.air_bottom.value()
        Nleft = self.air_left.value()
        if not self.manual_air.isChecked():  # use same air for all edges
            if self.connection_side == 2:
                hold = Nleft
            else:
                hold = Ntop
            Ntop = hold
            Nright = hold
            Nbottom = hold
            Nleft = hold

        mesh = [Ntop, Nright, Nbottom, Nleft, Nx, Ny]
        if self.connection_side != -1:
            mesh[(self.connection_side+2) % 4] = 0

        if self.connection_side == 0:
            y -= height
        elif self.connection_side == 3:
            x -= width

        other_data = {'type': 'rectangle'}
        return (x, y, width, height), Mesh(mesh, other_data)

    def for_expanding(self, prim, side_code):
        """
        Расширяем фигуру, пристраивая прямоугольник со стороны side_code к prim

        side_code:
            0 - вверх
            1 - справа
            2 - низ
            3 - слева
        """
        self.connection_side = side_code
        pos = [self.x, self.y]
        dim = [self.width, self.height]
        air = [self.air_top, self.air_right, self.air_bottom, self.air_left]
        fig = [self.Nx, self.Ny]
        prim_pos = [prim.x, prim.y]
        fixed_pos = [prim.y, prim.x + prim.width, prim.y + prim.height, prim.x]
        prim_dim = [prim.width, prim.height]
        prim_stp = [prim.step_x, prim.step_y]
        prim_bounds = [(prim.x, prim.x + prim.width),
                       (prim.y, prim.y + prim.height)]
        nodes = [prim.mesh[4], prim.mesh[5]]  # mesh[4] is x

        free_axis = side_code % 2  # ось, по которой можно двигать примитив
        to_prim = (side_code+2) % 4  # сторона, с которой находится prim

        pos[free_axis].setValue(prim_pos[free_axis])
        pos[free_axis].setSingleStep(prim_stp[free_axis])
        pos[not free_axis].setValue(fixed_pos[side_code])
        pos[not free_axis].setEnabled(False)

        air[to_prim].hide()

        dim[free_axis].setValue(prim_dim[free_axis])
        dim[free_axis].setSingleStep(prim_stp[free_axis])  # help with scale
        dim[not free_axis].setValue(prim_stp[not free_axis])
        dim[not free_axis].setSingleStep(prim_stp[not free_axis])

        fig[free_axis].setValue(nodes[free_axis] + 1)  # +1 - go back to nodes
        fig[free_axis].setEnabled(False)
        self.wath_node(fig[free_axis], prim_stp[free_axis])
        con_min, con_max = prim_bounds[free_axis]
        self.wath_connection(pos[free_axis], con_min, con_max, free_axis == 1)

        if side_code == 2:  # air_top was default, but now it disabled
            self.air_left.setEnabled(True)

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


class NewTriangleWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        uic.loadUi('ui/new_triangle.ui', self)

        self.comboBox.currentIndexChanged.connect(self.select_type)

    def select_type(self, index):
        boxes = [self.air_top, self.air_left, self.air_right, self.air_bottom]
        states = [False, True, False, True]
        if index == 1:
            states = [False, False, True, True]
        if index == 2:
            states = [True, True, False, False]
        if index == 3:
            states = [True, False, True, False]

        for i in range(0, 4):
            boxes[i].setEnabled(states[i])

    def get_data(self):
        x = self.x.value()
        y = self.y.value()
        width = self.width.value()
        height = self.height.value()

        Nx = self.Nx.value() - 1  # '-1': proceed in blocks, not nodes
        Ny = self.Ny.value() - 1
        Ntop = self.air_top.value()  # no '-1' because 1 node belong to figure
        Nright = self.air_right.value()
        Nbottom = self.air_bottom.value()
        Nleft = self.air_left.value()
        mesh = [Ntop, Nright, Nbottom, Nleft, Nx, Ny]
        other_data = {'type': 'triangle', 'form': self.comboBox.currentIndex()}

        return (x, y, width, height), Mesh(mesh, other_data)
