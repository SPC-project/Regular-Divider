from PyQt5.QtGui import QColor
from PyQt5.QtCore import QPoint
import abc


class Mesh:
    """ Auxiliary abstraction for finite-elemental grid """
    def __init__(self, grid, other=None):
        # NAT, NAR, NAB, NAL: amount of air blocks at Top/Right/Bottom/Left
        # NFX, NFY: amount of figure blocks for width and height
        # 'Block' — two combined in square elements (::).
        #   top-left bottom-right diagonal is connection between them
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


class AbstractPrimitive:
    __metaclass__ = abc.ABCMeta

    COL_AIR = QColor(0, 0, 255, 127)
    COL_FIG = QColor(0, 0, 0)
    COL_FIG_INNNER = QColor(0, 0, 0, 64)
    EXPORT_DESCRIPTION = "type: "
    AIR_CODE = 0
    FIGURE_CODE = 1

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
        self.end_y = self.y + self.step_y*height

    @abc.abstractmethod
    def update_me(self):
        pass

    def connect(self, edge, neighbour):
        if not neighbour:
            raise ValueError("Пропущен второй аргумент (neighbour)")

        self.binds[edge] = neighbour
        for i in range(4):
            if self.binds[i]:
                self.mesh.set_val_at(i, 0)

        self.modify()

    def get_box(self):
        return (self.start_x, self.start_y, self.end_x, self.end_y)

    def export_figure(self, to):
        """
        Save primitive to curr_text file as (single line):
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

    def draw_rect_mesh(self, canvas, grid_x, grid_y, grid_width, grid_height):
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

    @abc.abstractmethod
    def save_mesh(self, output):
        """
        output.element(A, B, C) — записать индексы вершин, образующих элемент
        output.coordinates — абсцисса и ордината вершин (номер строки = индекс вершины).
            Два действительных числа в ряд
        output.elements_material — код для материала элемента (0 — воздух, 1 — фигура)
            Номер строки в этом файле соответствует номеру строки элемента в ind_f
        output.nodes_material — код для материала узла
            Номер строки в этом файле соответствует номеру строки узла в coor_f

        output.last_index — индекс последнего существующего узла сетки разбиения
        """
        pass

    def save_rectangle_mesh(self, nwidth, nheight, output, x0, y0, dx, dy, m=None):
        """
        nwidth, nheight — количество квадратов в ширину\высоту
           Квадрат делится диагональю на элементы. Узлов на один больше чем квадратов
        output — словарь с текстовыми дескрипторами (см. save_mesh)
        x0, y0 — координаты начала элемента
        dx, dy — self.step_x, self.step_y
        """
        index = output.last_index
        if m is None:
            m = self.FIGURE_CODE

        # Записываем тройки индексов узлов, образующих треугольники
        for j in range(nheight):
            shift = nwidth + 1  # shift to next layer of mesh's grid
            for i in range(nwidth):
                current = index + i + shift*j
                output.save_element(current, current + shift, current + shift + 1, m)
                output.save_element(current, current + 1, current + shift + 1, m)

        # Координаты узлов
        for j in range(nheight+1):  # Узлов на один больше чем квадратов
            for i in range(nwidth+1):
                output.save_node(x0 + dx*i, y0 + dy*j)

    def __str__(self):
        return "{}, {} | {}".format(self.start_x, self.start_y, self.mesh)
