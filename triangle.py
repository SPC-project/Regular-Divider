from primitive import AbstractPrimitive
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor, QPolygon, QBrush


class Triangle(AbstractPrimitive):
    """
    Primitive figure, a rectangle
    """
    def __init__(self, fig, mesh):
        """
        """
        self.binds = [None]*4
        super(Triangle, self).__init__(fig, mesh)

    def modify(self):
        """
            Triangle types: :. | .: | ˸˙ | ˙˸
            Store vertexes as { most left, most rith, third };
                those at the top go first
        """
        self.vertexes = list()
        most_left = QPoint(self.x, self.y)
        most_right = QPoint(self.x + self.width, self.y)
        third = QPoint(self.x, self.y + self.height)
        form = self.mesh.data['form']
        if form == 1:
            most_left.setY(self.y + self.height)
            third.setX(self.x + self.width)
        elif form == 0:
            most_right.setY(self.y + self.height)
        elif form == 3:
            third.setX(self.x + self.width)

        self.vertexes.append(most_left)
        self.vertexes.append(most_right)
        self.vertexes.append(third)

    def generate_scaler(self, shift_x, shift_y, kx, ky):
        def scaler(point):
            x = int(round(kx*(shift_x + point.x())))
            y = int(round(ky*(shift_y + point.y())))
            return x, y
        return scaler

    def draw_figure(self, canvas, shift_x, shift_y, kx, ky):
        canvas.setPen(Qt.black)

        scale = self.generate_scaler(shift_x, shift_y, kx, ky)

        def convert_line(A, B):
            start_x, start_y = scale(A)
            end_x, end_y = scale(B)
            return start_x, start_y, end_x, end_y

        l1 = self.vertexes[0]
        l2 = self.vertexes[1]
        l3 = self.vertexes[2]
        canvas.drawLine(*convert_line(l1, l2))
        canvas.drawLine(*convert_line(l2, l3))
        canvas.drawLine(*convert_line(l3, l1))

    def draw_mesh(self, canvas, shift_x, shift_y, kx, ky):
        """ pixel_[x/y]: insert node index, get x/y coordinate of it """
        COL_AIR = QColor(0, 0, 255, 127)
        COL_FIG = Qt.black
        COL_FIG_INNNER = QColor(0, 0, 0, 64)

        canvas.setPen(COL_FIG)
        canvas.setBrush(QBrush(COL_FIG_INNNER))

        triangle = QPolygon()
        scale = self.generate_scaler(shift_x, shift_y, kx, ky)
        for vertex in self.vertexes:
            x, y = scale(vertex)
            triangle.append(QPoint(x, y))
        triangle.append(triangle.first())  # close the polygon
        canvas.drawPolygon(triangle, 4)
