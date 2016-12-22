from primitive import AbstractPrimitive
from PyQt5.QtCore import Qt, QPoint


class Triangle(AbstractPrimitive):
    """
    Primitive figure, a rectangle
    """
    def __init__(self, fig, mesh):
        """
        """
        super(Triangle, self).__init__(fig, mesh)
        self.binds = [None]*4

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
        if self.triangle_type == 1:
            most_left.setY(self.y + self.height)
        if self.triangle_type == 0:
            most_right.setY(self.y + self.height)
        if self.triangle_type == 1 or self.triangle_type == 3:
            most_right.setX(self.x + self.width)

        self.vertexes.append(most_left)
        self.vertexes.append(most_right)
        self.vertexes.append(third)

    def draw_figure(self, canvas, shift_x, shift_y, kx, ky):
        canvas.setPen(Qt.black)

        def scale_x(pos_x):
            return int(round(kx*(shift_x + pos_x)))

        def scale_y(pos_y):
            return int(round(ky*(shift_y + pos_y)))

        def convert_line(A, B):
            start_x = scale_x(A.x())
            start_y = scale_y(A.y())
            end_x = scale_x(B.x())
            end_y = scale_y(B.y())
            return start_x, start_y, end_x, end_y

        l1 = self.vertexes[0]
        l2 = self.vertexes[1]
        l3 = self.vertexes[2]
        canvas.drawLine(*convert_line(l1, l2))
        canvas.drawLine(*convert_line(l2, l3))
        canvas.drawLine(*convert_line(l3, l1))

    def draw_mesh(self, canvas, pixel_x, pixel_y):
        pass
