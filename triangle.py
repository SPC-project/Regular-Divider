from primitive import AbstractPrimitive
from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtGui import QPolygon, QBrush


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

    def generate_scaler(self):
        def scaler(point):
            x = point.x()
            y = point.y()
            return self.scale_x(x), self.scale_y(y)
        return scaler

    def draw_figure(self, canvas):
        canvas.setPen(self.COL_FIG)
        scale = self.generate_scaler()

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

    def draw_mesh(self, canvas):
        # Make a rectangle with one diagonal (upper-left bottom-right)
        tile_w = self.step_x * self.drawing_coefs['kx']
        tile_h = self.step_y * self.drawing_coefs['ky']
        dual_element = QPolygon(QRect(0, 0, tile_w, tile_h), True)
        dual_element.putPoints(5, tile_w, tile_h)  # insert sixth vertex
        canvas.drawPolygon(dual_element)

        # Fill the figure
        the_figure = QPolygon()
        scale = self.generate_scaler()
        for vertex in self.vertexes:
            x, y = scale(vertex)
            the_figure.append(QPoint(x, y))
        the_figure.append(the_figure.first())  # close the polygon
        canvas.setPen(self.COL_FIG)
        canvas.setBrush(QBrush(self.COL_FIG_INNNER))  # drawPolygon() use it
        canvas.drawPolygon(the_figure)

    def draw_rect_mesh(self, canvas, tile, dx, dy,
                       node_start_x, node_start_y, node_end_x, node_end_y):
        pass
