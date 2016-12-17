from primitive import AbstractPrimitive
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QColor


class Triangle(AbstractPrimitive):
    """
    Primitive figure, a rectangle
    """
    def __init__(self, fig, mesh):
        """
        """
        self.binds = [None]*4
        self.modify(fig, mesh)

    def modify(self, fig, mesh):
        x, y, width, height = fig
        self.x, self.y, self.width, self.height = fig
        Ntop, Nright, Nbottom, Nleft, Nx, Ny, self.triangle_type = mesh
        self.vertexes = list()
        if self.triangle_type == 0:
            self.vertexes.append(QPoint(x, y))
            self.vertexes.append(QPoint(x+width, y+height))
            self.vertexes.append(QPoint(x, y+height))
        elif self.triangle_type == 1:
            self.vertexes.append(QPoint(x, y+height))
            self.vertexes.append(QPoint(x+width, y))
            self.vertexes.append(QPoint(x+width, y+height))
        elif self.triangle_type == 2:
            self.vertexes.append(QPoint(x, y))
            self.vertexes.append(QPoint(x+width, y))
            self.vertexes.append(QPoint(x, y+height))
        elif self.triangle_type == 3:
            self.vertexes.append(QPoint(x, y))
            self.vertexes.append(QPoint(x+width, y))
            self.vertexes.append(QPoint(x+width, y+height))

        self.mesh = mesh

    def draw_figure(self, canvas, shift_x, shift_y, kx, ky):
        canvas.setPen(Qt.black)

        def convert_x(pos_x):
            return int(round(kx*(shift_x + pos_x)))

        def convert_y(pos_y):
            return int(round(ky*(shift_y + pos_y)))

        def convert_line(A, B):
            start_x = convert_x(A.x())
            start_y = convert_y(A.y())
            end_x = convert_x(B.x())
            end_y = convert_y(B.y())
            return start_x, start_y, end_x, end_y

        l1 = self.vertexes[0]
        l2 = self.vertexes[1]
        l3 = self.vertexes[2]
        canvas.drawLine(*convert_line(l1, l2))
        canvas.drawLine(*convert_line(l2, l3))
        canvas.drawLine(*convert_line(l3, l1))

    def draw_mesh(self, canvas, pixel_x, pixel_y):
        pass
