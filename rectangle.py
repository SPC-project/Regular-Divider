from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDialog
from PyQt5 import uic

NAT = 0
NAR = 1
NAB = 2
NAL = 3
NX = 4
NY = 5


class Rectangle:
    """
    Primitive figure, a rectangle
    """
    def __init__(self, fig, mesh):
        """
        fig: tuple of rectangle - (x, y, width, hegiht)
        mesh: specify how to divide @fig, list - [NAT, NAR, NAB, NAL, NX, NY]
            NAT - how many air elements at the top of @fig
            NAR - air elements at right
            NAB - air elements at bottom
            NAL - air elements at left
            NX - count of fig's elements by width
            NY - count of fig's elements by height
        """
        self.binds = [None]*4
        self.modify(fig, mesh)

    def modify(self, fig, mesh):
        self.x, self.y, self.width, self.height = fig
        self.mesh = mesh

        # if has connection to another Rectangles, 'shave' that edge from air
        for i in range(4):
            if self.binds[i]:
                self.mesh[i] = 0

        self.element_count_w = mesh[NAL] + mesh[NX] + mesh[NAR]
        self.element_count_h = mesh[NAT] + mesh[NY] + mesh[NAB]
        self.step_x = self.width/mesh[NX]
        self.step_y = self.height/mesh[NY]
        self.start_x = self.x - self.step_x*mesh[NAL]  # where air start
        self.start_y = self.y - self.step_y*mesh[NAT]

    def get_box(self):
        end_x = self.x + self.step_x*(self.mesh[NX] + self.mesh[NAR])
        end_y = self.y + self.step_y*(self.mesh[NY] + self.mesh[NAB])
        return (self.start_x, self.start_y, end_x, end_y)

    def shave_air(self, edge, neighbour):
        if not neighbour:
            raise ValueError("Пропущен второй аргумент (neighbour)")
        self.binds[edge] = neighbour
        fig = (self.x, self.y, self.width, self.height)
        self.modify(fig, self.mesh)

    def draw(self, canvas, mesh_canvas, shift_x, shift_y, kx, ky):
        def pixel_x(n_elements):
            val = shift_x + self.start_x + n_elements*self.step_x
            return int(round(val*kx))

        def pixel_y(n_elements):
            val = shift_y + self.start_y + n_elements*self.step_y
            return int(round(val*ky))

        self.draw_figure(canvas, shift_x, shift_y, kx, ky)
        self.draw_mesh(mesh_canvas, pixel_x, pixel_y)

    def draw_figure(self, canvas, shift_x, shift_y, kx, ky):
        canvas.setPen(Qt.black)
        x = int(round((shift_x + self.x)*kx))
        y = int(round((shift_y + self.y)*ky))
        w = int(round(self.width*kx))
        h = int(round(self.height*ky))
        canvas.drawRect(x, y, w, h)

    def draw_mesh(self, canvas, pixel_x, pixel_y):
        """
        Split rectangle to smaller rectangles step_x*step_y,
        then for each draw diagonal
        """
        M = self.mesh
        X1 = M[NAL]
        Y1 = M[NAT]
        X2 = M[NAL] + M[NX]  # start of right air layer
        Y2 = M[NAT] + M[NY]  # start of bottom air layer
        X_NLEN = X2 + M[NAR]
        Y_NLEN = Y2 + M[NAB]
        COL_AIR = QColor(0, 0, 255, 127)
        COL_FIG = Qt.black
        COL_FIG_INNNER = QColor(0, 0, 0, 64)
        A = QPoint()
        B = QPoint()

        # Horizontal lines (3 segments: air, figure, air)
        x0 = pixel_x(0)
        x1 = pixel_x(X1)
        x2 = pixel_x(X2)
        x3 = pixel_x(X_NLEN)
        for j in range(Y_NLEN+1):  # +1 because N segments defined by N+1 dots
            y = pixel_y(j)
            A.setY(y)
            B.setY(y)
            B.setX(x0)
            for xi in (x1, x2, x3):
                A.setX(B.x())
                B.setX(xi)
                if xi == x2 and j >= Y1 and j <= Y2:
                    canvas.setPen(COL_FIG)
                else:
                    canvas.setPen(COL_AIR)
                canvas.drawLine(A, B)

        # Vertical lines
        y0 = pixel_y(0)
        y1 = pixel_y(Y1)
        y2 = pixel_y(Y2)
        y3 = pixel_y(Y_NLEN)
        for i in range(X_NLEN+1):
            x = pixel_x(i)
            A.setX(x)
            B.setX(x)
            B.setY(y0)
            for yi in (y1, y2, y3):
                A.setY(B.y())
                B.setY(yi)
                if yi == y2 and i >= X1 and i <= X2:
                    canvas.setPen(COL_FIG)
                else:
                    canvas.setPen(COL_AIR)
                canvas.drawLine(A, B)

        # Diagonal lines
        for i in range(X_NLEN):  # no need +1: one diagonal for every rectangle
            x = pixel_x(i)
            y = pixel_y(0)
            B.setY(y)
            A.setX(x)
            for j in range(Y_NLEN):
                A.setY(B.y())
                x = pixel_x(i+1)
                y = pixel_y(j+1)
                B.setX(x)
                B.setY(y)
                if X1 <= i and i < X2 and Y1 <= j and j < Y2:
                    canvas.setPen(COL_FIG)
                    canvas.fillRect(QRect(A, B), COL_FIG_INNNER)
                else:
                    canvas.setPen(COL_AIR)
                canvas.drawLine(A, B)

    def save_indexes(self, f, index_start):
        x_elem = self.element_count_w - 1
        y_elem = self.element_count_h - 1
        x_nodes = self.element_count_w
        y_nodes = self.element_count_h
        # N отрезков создаются N+1 точками - будем добавлять 1 в конце цепочки
        if not self.binds[NAR]:
            x_nodes += 1
            x_elem += 1
        if not self.binds[NAB]:
            y_nodes += 1
            y_elem += 1

        self.index_start = index_start
        self.problem_zone_first_index = self.index_start + x_nodes*y_nodes

        # Divide self to rectangular grid and split every rectangle by diagonal
        for j in range(y_elem):
            for i in range(x_elem):
                # +1 because node indexing start from 1, not 0
                first_ind = index_start + i + j*x_nodes + 1
                second_ind = index_start + (i+1) + j*x_nodes + 1
                third_ind = index_start + (i+1) + (j+1)*x_nodes + 1
                forth_ind = index_start + i + (j+1)*x_nodes + 1
                f.write("{} {} {}\n".format(first_ind, second_ind, third_ind))
                f.write("{} {} {}\n".format(first_ind, third_ind, forth_ind))

        return self.problem_zone_first_index

    def deal_with_horizontal_contact_regions(self, f, index, sewing_nodes, material):
        if not self.binds[NAR]:
            return index

        he = self.binds[NAR]
        dy = self.step_y  # step_y should be same
        end_self = self.start_y + self.element_count_h * dy
        end_he = he.start_y + he.element_count_h * dy

        W_self = self.element_count_w  # here element_count_w fine
        W_he = he.element_count_w + 1  # need nodes_count_w, actually
        SEW_X = self.start_x + W_self*self.step_x
        fig_start_self = self.start_y + self.mesh[NAT]*dy
        fig_end_self = fig_start_self + self.mesh[NY]*dy
        fig_start_he = he.start_y + he.mesh[NAT]*dy
        fig_end_he = fig_start_he + he.mesh[NY]*dy

        iterate_count = int((end_self-self.start_y) / dy)
        offset_he = int((he.start_y - self.start_y) / dy)
        created = False
        added1 = False
        left1_is_air = True
        left2_is_air = True
        right1_is_air = True
        right2_is_air = True
        for j in range(iterate_count):
            left1_is_air = True
            left2_is_air = True
            right1_is_air = True
            right2_is_air = True
            pos = self.start_y + j*dy
            left_node_1 = self.index_start + (j+1)*W_self  # TODO be wise rename step_y to dy (misspell with start_y)
            left_node_2 = self.index_start + (j+2)*W_self

            if fig_start_self <= pos and pos <= fig_end_self:
                left1_is_air = False
            if fig_start_self <= pos+dy and pos+dy <= fig_end_self:
                left2_is_air = False

            if he.start_y <= pos and pos <= end_he:
                right_node_1 = he.index_start + (j-offset_he)*W_he + 1
                if fig_start_he <= pos and pos <= fig_end_he:
                    right1_is_air = False
            else:
                index += 1
                right_node_1 = index
                new_node = (index, SEW_X, pos)
                sewing_nodes.append(new_node)
                created = False
                added1 = True

            if he.start_y <= pos+dy and pos+dy <= end_he:
                right_node_2 = he.index_start + (j-offset_he+1)*W_he + 1
                if fig_start_he <= pos+dy and pos+dy <= fig_end_he:
                    right2_is_air = False
            else:
                right_node_2 = index + 1
                new_node = (index+1, SEW_X, pos+dy)
                created = True
                sewing_nodes.append(new_node)

            f.write("{} {} {}\n".format(left_node_1, right_node_1, right_node_2))

            if added1:
                added1 = False
                if left1_is_air and right1_is_air:
                    material.append(0)
                else:
                    material.append(1)
            f.write("{} {} {}\n".format(left_node_1, left_node_2, right_node_2))

        if created:
            index += 1
            if left2_is_air and right2_is_air:
                material.append(0)
            else:
                material.append(1)

        return index

    def deal_with_vertical_contact_regions(self, f, index, sewing_nodes, material):
        if not self.binds[NAB]:
            return index

        he = self.binds[NAB]
        dx = self.step_x  # step_y should be same
        end_he = he.start_x + he.element_count_w * dx

        fig_start_self = self.start_x + self.mesh[NAL]*dx
        fig_end_self = fig_start_self + self.mesh[NX]*dx
        fig_start_he = he.start_x + he.mesh[NAL]*dx
        fig_end_he = fig_start_he + he.mesh[NX]*dx

        SEW_Y = self.start_y + self.element_count_h*self.step_y
        offset_self = (self.element_count_w+1)*(self.element_count_h-1)
        offset_he = int((he.start_x - self.start_x) / dx)
        created = False
        added1 = False
        left1_is_air = True
        left2_is_air = True
        right1_is_air = True
        right2_is_air = True
        for i in range(self.element_count_w):
            pos = self.start_x + i*dx
            left_node_1 = self.index_start + offset_self + i + 1
            left_node_2 = self.index_start + offset_self + i+2
            left1_is_air = True
            left2_is_air = True
            right1_is_air = True
            right2_is_air = True
            if fig_start_self <= pos and pos <= fig_end_self:
                left1_is_air = False
            if fig_start_self <= pos+dx and pos+dx <= fig_end_self:
                left2_is_air = False

            if he.start_x <= pos and pos <= end_he:
                right_node_1 = he.index_start + i-offset_he + 1
                if fig_start_he <= pos and pos <= fig_end_he:
                    right1_is_air = False
            else:
                index += 1
                right_node_1 = index
                new_node = (index, pos, SEW_Y)
                sewing_nodes.append(new_node)
                created = False
                added1 = True

            if he.start_x <= pos+dx and pos+dx <= end_he:
                right_node_2 = he.index_start + i-offset_he+1 + 1
                if fig_start_he <= pos+dx and pos+dx <= fig_end_he:
                    right2_is_air = False
            else:
                right_node_2 = index + 1
                new_node = (index+1, pos+dx, SEW_Y)
                sewing_nodes.append(new_node)
                created = True

            f.write("{} {} {}\n".format(left_node_1, right_node_1, right_node_2))
            if added1:
                added1 = False
                if left1_is_air and right1_is_air:
                    material.append(0)
                else:
                    material.append(1)
            f.write("{} {} {}\n".format(left_node_1, left_node_2, right_node_2))

        if created:
            index += 1
            if left2_is_air and right2_is_air:
                material.append(0)
            else:
                material.append(1)

        return index

    def save_coor(self, f):
        x_nodes = self.element_count_w
        y_nodes = self.element_count_h
        # N отрезков создаются N+1 точками - будем добавлять 1 в конце цепочки
        if not self.binds[NAR]:
            x_nodes += 1
        if not self.binds[NAB]:
            y_nodes += 1
        for j in range(y_nodes):
            y = self.start_y + j*self.step_y
            for i in range(x_nodes):
                x = self.start_x + i*self.step_x
                f.write("{} {}\n".format(x, y))

    def save_material(self, f):
        x_nodes = self.element_count_w
        y_nodes = self.element_count_h
        if not self.binds[NAR]:
            x_nodes += 1
        if not self.binds[NAB]:
            y_nodes += 1
        M = self.mesh
        X1 = M[NAL]
        Y1 = M[NAT]
        X2 = X1 + M[NX]  # start of right air layer
        Y2 = Y1 + M[NY]  # start of bottom air layer

        for j in range(y_nodes):
            in_figure_y = j >= Y1 and j <= Y2
            for i in range(x_nodes):
                in_figure_x = i >= X1 and i <= X2
                if in_figure_x and in_figure_y:
                    f.write("1\n")  # Figure's flag
                else:
                    f.write("0\n")  # Air

    def save_material_of_element(self, f):
        M = self.mesh
        X1 = M[NAL]
        Y1 = M[NAT]
        X2 = X1 + M[NX]  # start of right air layer
        Y2 = Y1 + M[NY]  # start of bottom air layer
        for j in range(self.element_count_h):
            in_figure_y = j >= Y1 and j < Y2
            for i in range(self.element_count_w):
                in_figure_x = i >= X1 and i < X2
                if in_figure_x and in_figure_y:
                    f.write("1\n")  # Figure's flag
                    f.write("1\n")  # Figure's flag
                else:
                    f.write("0\n")  # Air
                    f.write("0\n")  # Air


class NewRectangleDialog(QDialog):
    """
    Важно: пользователь вводит количество узлов, но программе работать удобнее
    с "квадратами" (по диагонали которого впоследствии образуется два элемента)
    Так что при переходе туда-обратно придется прибавлять\отнимать единицу
    """
    def __init__(self):
        QDialog.__init__(self)
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
            print("move", x, width)
            x -= width

        return (x, y, width, height), mesh,

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


