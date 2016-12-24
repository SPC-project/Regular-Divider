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
        M = self.mesh
        # Make a rectangle with one diagonal (upper-left bottom-right)
        tile_w = self.step_x * self.drawing_coefs['kx']
        tile_h = self.step_y * self.drawing_coefs['ky']

        # Draw air
        canvas.setPen(self.COL_AIR)
        if M.NAL != 0:
            x, y, w, h = 0, 0, M.NAL, M.NFY + M.NAB
            self.draw_rect_mesh(canvas, tile_w, tile_h, x, y, w, h)
        if M.NAB != 0:
            x, y, w, h = M.NAL, M.NAT + M.NFY, M.NFX, M.NAB
            self.draw_rect_mesh(canvas, tile_w, tile_h, x, y, w, h)

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

    def draw_rect_mesh(self, canvas, dx, dy,
                       grid_x, grid_y, grid_width, grid_height):
        tile = QPolygon(QRect(0, 0, dx, dy), True)
        tile.putPoints(5, dx, dy)  # insert sixth vertex, for diagonal
        x0 = self.pixel_x(grid_x)
        y0 = self.pixel_y(grid_y)
        tile.translate(x0, y0)

        backward_x = -grid_width*dx
        for j in range(grid_height):
            for i in range(grid_width):
                canvas.drawPolygon(tile)
                tile.translate(dx, 0)
            tile.translate(backward_x, dy)
