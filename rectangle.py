from PyQt5.QtCore import Qt, QPoint
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

    def shave_air(self, edge, neighbour):
        if not neighbour:
            raise ValueError("Пропущен второй аргумент (neighbour)")
        self.binds[edge] = neighbour
        fig = (self.x, self.y, self.width, self.height)
        self.modify(fig, self.mesh)

    def draw(self, canvas, mesh_canvas, shift_x, shift_y, kx, ky):
        def pixel_x(n_elements):
            val = shift_x + self.start_x + n_elements*self.step_x
            return int(val*kx)

        def pixel_y(n_elements):
            val = shift_y + self.start_y + n_elements*self.step_y
            return int(val*ky)

        self.draw_figure(canvas, shift_x, shift_y, kx, ky)
        self.draw_mesh(mesh_canvas, pixel_x, pixel_y)

    def draw_figure(self, canvas, shift_x, shift_y, kx, ky):
        canvas.setPen(Qt.black)
        x = int((shift_x + self.x)*kx)
        y = int((shift_y + self.y)*ky)
        w = int(self.width*kx)
        h = int(self.height*ky)
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
        COL_AIR = Qt.blue
        COL_FIG = Qt.green
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
                if X1 <= i and i < X2 and Y1 <= j and j < Y2:
                    canvas.setPen(COL_FIG)
                else:
                    canvas.setPen(COL_AIR)
                A.setY(B.y())
                x = pixel_x(i+1)
                y = pixel_y(j+1)
                B.setX(x)
                B.setY(y)
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

    def deal_with_horizontal_contact_regions(self, f, index):
        if not self.binds[NAR]:
            return index

        he = self.binds[NAR]
        dy = self.step_y  # step_y should be same
        end_self = self.start_y + self.element_count_h * dy
        end_he = he.start_y + he.element_count_h * dy

        W_self = self.element_count_w  # here element_count_w fine
        W_he = he.element_count_w + 1  # need nodes_count_w, actually

        iterate_count = int((end_self-self.start_y) / dy)
        offset_he = int((he.start_y - self.start_y) / dy)
        for j in range(iterate_count):
            pos = self.start_y + j*dy
            if self.start_y <= pos and pos <= end_self:  # TODO be wise rename step_y to dy (misspell with start_y)
                left_node_1 = self.index_start + (j+1)*W_self
            else:
                index += 1
                left_node_1 = index

            if he.start_y <= pos and pos <= end_he:
                right_node_1 = he.index_start + (j-offset_he)*W_he + 1
            else:
                index += 1
                right_node_1 = index

            if self.start_y <= pos+dy and pos+dy <= end_self:
                left_node_2 = self.index_start + (j+2)*W_self
            else:
                left_node_2 = index + 1

            if he.start_y <= pos+dy and pos+dy <= end_he:
                right_node_2 = he.index_start + (j-offset_he+1)*W_he + 1
            else:
                right_node_2 = index + 1

            f.write("{} {} {}\n".format(left_node_1, right_node_1, right_node_2))
            f.write("{} {} {}\n".format(left_node_1, left_node_2, right_node_2))

        return index

    def deal_with_vertical_contact_regions(self, f, index):
        if not self.binds[NAB]:
            return index

        he = self.binds[NAB]
        dx = self.step_x  # step_y should be same
        end_self = self.start_x + self.element_count_w * dx
        end_he = he.start_x + he.element_count_w * dx

        W_self = self.element_count_w  # here element_count_w fine
        W_he = he.element_count_w + 1  # need nodes_count_w, actually

        offset_self = (self.element_count_w+1)*(self.element_count_h-1)
        offset_he = int((he.start_x - self.start_x) / dx)
        for i in range(self.element_count_w):
            pos = self.start_x + i*dx
            if self.start_x <= pos and pos <= end_self:  # TODO be wise rename step_y to dy (misspell with start_y)
                left_node_1 = self.index_start + offset_self + i + 1
            else:
                index += 1
                left_node_1 = index

            if he.start_x <= pos and pos <= end_he:
                right_node_1 = he.index_start + i-offset_he + 1
            else:
                index += 1
                right_node_1 = index

            if self.start_x <= pos+dx and pos+dx <= end_self:
                left_node_2 = self.index_start + offset_self + i+2
            else:
                left_node_2 = index + 1

            if he.start_x <= pos+dx and pos+dx <= end_he:
                right_node_2 = he.index_start + i-offset_he+1 + 1
            else:
                right_node_2 = index + 1

            f.write("{} {} {}\n".format(left_node_1, right_node_1, right_node_2))
            f.write("{} {} {}\n".format(left_node_1, left_node_2, right_node_2))

        return index
    def save(self, f, index_start):
        """
        Сохраняем примитив, записывая координаты узлов, индексы вершин
            элементов и материал узлов/элементов

        Если он с кем-то граничит, то узлы левой/нижней границы отходят
            соседнему, а правой/верхней - себе. Если какие-то из граничных
            узлов ни с чем не соприкасаются - их прибавляют себе

        """
        x_elems = self.element_count_w
        y_elems = self.element_count_h
        x_nodes = x_elems
        y_nodes = y_elems


        self.problem_zone_first_index = x_nodes*y_nodes
        self.index_start = index_start

        M = self.mesh
        X1 = M[NAL]
        Y1 = M[NAT]
        X2 = X1 + M[NX]  # start of right air layer
        Y2 = Y1 + M[NY]  # start of bottom air layer
        X_NLEN = X2 + M[NAR]
        Y_NLEN = Y2 + M[NAB]

        for j in range(Y_NLEN):
            for i in range(X_NLEN):
                # +1 because node indexing start from 1, not 0
                first_ind = index_start + i + j*x_nodes + 1
                second_ind = index_start + (i+1) + j*x_nodes + 1
                third_ind = index_start + (i+1) + (j+1)*x_nodes + 1
                forth_ind = index_start + i + (j+1)*x_nodes + 1
                f.write("{} {} {}\n".format(first_ind, second_ind, third_ind))
                f.write("{} {} {}\n".format(first_ind, third_ind, forth_ind))

        for i in range(x_nodes):
            x = i*self.step_x
            for j in range(Y_nodes):
                y = j*self.step_y
                f.write("{} {}\n".format(x, y))

        for j in range(Y_nodes):
            in_figure_y = j >= Y1 and j <= Y2
            for i in range(x_nodes):
                in_figure_x = i >= X1 and i <= X2
                if in_figure_x and in_figure_y:
                    f.write("1\n")  # Figure's flag
                else:
                    f.write("0\n")  # Air

        for j in range(Y_NLEN):
            in_figure_y = j >= Y1 and j < Y2
            for i in range(X_NLEN):
                in_figure_x = i >= X1 and i < X2
                if in_figure_x and in_figure_y:
                    f.write("1\n")  # Figure's flag
                    f.write("1\n")  # Figure's flag
                else:
                    f.write("0\n")  # Air
                    f.write("0\n")  # Air
        return x_elems*y_elems*2, x_nodes*y_nodes


class NewRectangleDialog(QDialog):
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
