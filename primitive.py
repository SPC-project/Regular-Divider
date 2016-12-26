from PyQt5.QtWidgets import QDialog, QMessageBox, QWidget
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QPoint
from PyQt5 import uic

import abc


class Mesh:
    """ Auxiliary abstraction for finite-elemental grid """
    def __init__(self, grid, other=None):
        """
            NAT, NAR, NAB, NAL: [count of] Nodes Air at Top/Right/Bottom/Left
            NFX, NFY: [count of] Nodes Figure Width/Height
        """
        self.NAT, self.NAR, self.NAB, self.NAL, self.NFX, self.NFY = grid
        self.data = other
        if not other:
            self.data = {"type": "undefined"}

    def __str__(self):
        display = str(self.NAT) + " " + str(self.NAR) + " " + str(self.NAB) \
            + " " + str(self.NAL) + " " + str(self.NFX) + " " + str(self.NFY)
        return display + " " + str(self.data)

    def set_val_at(self, index, value):
        holder = [self.NAT, self.NAR, self.NAB, self.NAL, self.NFX, self.NFY]
        holder[index] = value
        self.NAT, self.NAR, self.NAB, self.NAL, self.NFX, self.NFY = holder


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
            self.Rectangle_widget.set_data(primitive)
        else:
            self.tabWidget.setCurrentIndex(1)
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

        Ntop = rectangle.mesh.NAT
        Nright = rectangle.mesh.NAR
        Nbottom = rectangle.mesh.NAB
        Nleft = rectangle.mesh.NAL
        Nx = rectangle.mesh.NFX
        Ny = rectangle.mesh.NFY
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
        nodes = [prim.mesh.NFX, prim.mesh.NFY]  # mesh[4] is x

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
        self.expanding_index = -1

    def select_type(self, index):
        boxes = [self.air_top, self.air_right, self.air_bottom, self.air_left]
        states = [False, False, True, True]
        text = self.comboBox.itemText(index)
        if text == ".:":
            states = [False, True, True, False]
        if text == "˸˙":
            states = [True, False, False, True]
        if text == "˙˸":
            states = [True, True, False, False]

        for i in range(0, 4):
            boxes[i].setEnabled(states[i])
            if not states[i]:
                boxes[i].setValue(0)

        if self.expanding_index != -1:
            connected_side = (self.expanding_index + 2) % 4
            boxes[connected_side].setEnabled(False)

    def set_data(self, triangle):
        pass

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
        forms = {":.": 0, ".:": 1, "˸˙": 2, "˙˸": 3}
        form = forms[self.comboBox.itemText(self.comboBox.currentIndex())]
        other_data = {'type': 'triangle', 'form': form}

        return (x, y, width, height), Mesh(mesh, other_data)

    def for_expanding(self, triangle, side_code):
        self.expanding_index = side_code
        if side_code == 0:
            # Index shift after removing => bigger first
            self.comboBox.removeItem(3)
            self.comboBox.removeItem(2)
            self.select_type(0)
        if side_code == 1:
            self.comboBox.removeItem(3)
            self.comboBox.removeItem(1)
            self.select_type(2)
        if side_code == 2:
            self.comboBox.removeItem(1)
            self.comboBox.removeItem(0)
            self.select_type(2)
            self.air_bottom.setEnabled(False)
        if side_code == 3:
            self.comboBox.removeItem(2)
            self.comboBox.removeItem(0)
            self.select_type(0)  # index moved because removeItem


class AbstractPrimitive:
    __metaclass__ = abc.ABCMeta

    COL_AIR = QColor(0, 0, 255, 127)
    COL_FIG = QColor(0, 0, 0)
    COL_FIG_INNNER = QColor(0, 0, 0, 64)
    EXPORT_DESCRIPTION = "type: "

    def __init__(self, fig, mesh):
        self.modify(fig, mesh)

    def modify(self, fig=None, mesh=None):
        if fig:
            self.x, self.y, self.width, self.height = fig
        if mesh:
            self.mesh = mesh

        self.update_me()

        self.element_count_w = self.mesh.NAL + self.mesh.NFX + self.mesh.NAR
        self.element_count_h = self.mesh.NAT + self.mesh.NFY + self.mesh.NAB
        self.step_x = self.width/self.mesh.NFX
        self.step_y = self.height/self.mesh.NFY
        self.start_x = self.x - self.step_x*self.mesh.NAL  # where air start
        self.start_y = self.y - self.step_y*self.mesh.NAT
        width = self.mesh.NFX + self.mesh.NAR
        height = self.mesh.NFY + self.mesh.NAB
        self.end_x = self.x + self.step_x*width
        self.end_y = self.y + self.step_y*(height)

    @abc.abstractmethod
    def update_me(self):
        pass

    def shave_air(self, edge, neighbour):
        if not neighbour:
            raise ValueError("Пропущен второй аргумент (neighbour)")
        self.binds[edge] = neighbour
        self.modify()

    def get_box(self):
        return (self.start_x, self.start_y, self.end_x, self.end_y)

    def draw(self, canvas, mesh_canvas, shift_x, shift_y, kx, ky):
        def sx(pos_x):
            val = shift_x + pos_x
            return int(round(val*kx))

        def sy(pos_y):
            val = shift_y + pos_y
            return int(round(val*ky))

        def tx(N):
            val = shift_x + self.start_x + N*self.step_x
            return int(round(val*kx))

        def ty(N):
            val = shift_y + self.start_y + N*self.step_y
            return int(round(val*ky))

        self.scale_x = sx  # Scale from world coordinates to canvas coordinates
        self.scale_y = sy
        self.pixel_x = tx  # Get the coordinate of Nth node
        self.pixel_y = ty
        self.drawing_coefs = {'shift_x': shift_x, 'shift_y': shift_x,
                              'kx': kx, 'ky': ky}
        self.draw_figure(canvas)
        self.draw_mesh(mesh_canvas)

    @abc.abstractmethod
    def draw_figure(self, canvas):
        pass

    @abc.abstractmethod
    def draw_mesh(self, canvas):
        pass

    def export_figure(self, to):
        """
        Save primitive to text file as (single line):
            type: <type> [| <other data>: <data>, ...]
            | x y w h | NAT NAR NAB NAL NFX NFY
        """
        txt = self.EXPORT_DESCRIPTION + "{}"
        to.write(txt.format(self.mesh.data["type"]))
        data_len = len(self.mesh.data)
        if data_len > 1:
            to.write(" | ")
            for key, value in self.mesh.data.items():
                if key != "type":
                    if data_len > 2:
                        to.write(", ")
                    to.write("{}: {}".format(key, value))
        x = self.x
        y = self.y
        w = self.width
        h = self.height
        to.write(" | {} {} {} {} | ".format(x, y, w, h))
        NAT = self.mesh.NAT
        NAR = self.mesh.NAR
        NAB = self.mesh.NAB
        NAL = self.mesh.NAL
        NFX = self.mesh.NFX
        NFY = self.mesh.NFY
        to.write("{} {} {} {} {} {}\n".format(NAT, NAR, NAB, NAL, NFX, NFY))

    def parse(data_about_primitive):
        """
        Get list of strings:
            [ 'type: <type>', '<other data>: <data>, ...', 'x y w h',
              'NAT NAR NAB NAL NFX NFY' ]
            <other data> is optional (use for Triangles to specify it's form)
        """
        offset = len(AbstractPrimitive.EXPORT_DESCRIPTION)
        prim_type = data_about_primitive[0][offset:]
        header = {'type': prim_type}
        if len(data_about_primitive) > 3:  # is <other data> section
            other_data = data_about_primitive[1].split(', ')
            for info in other_data:
                key, value = info.split(': ')
                if value.isdigit():
                    header[key] = int(value)  # Triangle's 'form' is integer
                else:
                    header[key] = value

        raw_fig = data_about_primitive[-2].split(' ')
        fig = tuple(float(value) for value in raw_fig[0:4])

        raw_grid = data_about_primitive[-1].split(' ')
        grid = tuple(int(value) for value in raw_grid[0:6])

        prim_type_index = 0
        if prim_type == "triangle":
            prim_type_index = 1
        return fig, Mesh(grid, header), prim_type_index

    def draw_rect_mesh(self, canvas, dx, dy,
                       grid_x, grid_y, grid_width, grid_height):
        """
        Draw rectangular region of mesh. First divide to squares,
            then draw diagonal and transform them to triangles
        'grid_*' arguments is numbers of nodes of the mesh
        """
        x0 = self.pixel_x(grid_x)
        y0 = self.pixel_y(grid_y)
        xn = self.pixel_x(grid_x + grid_width)
        yn = self.pixel_y(grid_y + grid_height)
        # Horizontal & diagonal lines
        A = QPoint(x0, y0)
        B = QPoint(xn, y0)
        canvas.drawLine(A, B)  # first line
        for j in range(1, grid_height+1):
            y = self.pixel_y(grid_y+j)
            A.setY(y)
            B.setY(y)
            canvas.drawLine(A, B)

        # Vertical lines
        A.setX(x0)
        B.setX(x0)
        A.setY(y0)
        B.setY(yn)
        canvas.drawLine(A, B)
        for i in range(1, grid_width+1):
            x = self.pixel_x(grid_x+i)
            A.setX(x)
            B.setX(x)
            canvas.drawLine(A, B)

        # Diagonal lines
        A.setX(x0)
        A.setY(y0)
        B.setX(self.pixel_x(grid_x + 1))  # Diagonal
        B.setY(self.pixel_y(grid_y + 1))
        for j in range(1, grid_height+1):
            for i in range(1, grid_width+1):
                canvas.drawLine(A, B)
                A.setX(self.pixel_x(grid_x + i))
                B.setX(self.pixel_x(grid_x + i + 1))
            A.setX(x0)
            A.setY(self.pixel_y(grid_y + j))
            B.setX(self.pixel_x(grid_x + 1))
            B.setY(self.pixel_y(grid_y + j + 1))
