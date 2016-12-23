from primitive import AbstractPrimitive
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor
import math


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
        """ pixel_[x/y]: insert node index, get x/y coordinate of it """
        M = self.mesh
        X1 = M.NAL            # start of figure's nodes
        Y1 = M.NAT
        X2 = M.NAL + M.NFX    # start of right air layer
        Y2 = M.NAT + M.NFY    # start of bottom air layer
        X_NLEN = X2 + M.NAR   # last node in row
        Y_NLEN = Y2 + M.NAB
        COL_AIR = QColor(0, 0, 255, 127)
        COL_FIG = Qt.black
        COL_FIG_INNNER = QColor(0, 0, 0, 64)
        A = QPoint()
        B = QPoint()

        hypotenuse = math.sqrt(self.width**2 + self.height**2)
        sin_alpha = self.width / hypotenuse
        cos_alpha = self.height / hypotenuse

        # Draw horizontal lines
        x0 = pixel_x(0)
        x1 = pixel_x(X1)
        x2 = pixel_x(X2)
        x3 = pixel_x(X_NLEN)
        for j in range(1, Y_NLEN+1):  # +1 because N segments defined by N+1 dots
            width_j = j*self.step_y*sin_alpha
            nodes = math.floor(width_j/self.step_x) + 1
            if nodes == 0:
                continue

            y = pixel_y(j)
            A.setY(y)
            B.setY(y)
            A.setX(x0)
            B.setX(pixel_x(nodes))
            canvas.drawLine(A, B)

        # Vertical lines
        y0 = pixel_y(0)
        y1 = pixel_y(Y1)
        y2 = pixel_y(Y2)
        y3 = pixel_y(Y_NLEN)
        for i in range(1, X_NLEN+1):
            height_i = i*self.step_y*cos_alpha
            nodes = math.floor(height_i/self.step_y) + 1
            if nodes == 0:
                continue

            x = pixel_x(X_NLEN-i)
            A.setX(x)
            B.setX(x)
            A.setY(pixel_y(Y_NLEN - nodes))
            B.setY(y3)
            canvas.drawLine(A, B)

        # Diagonal lines
        for i in range(1, X_NLEN+1):  # no need +1: one diagonal for every rectangle
            x = pixel_x(0)
            y = pixel_y(X_NLEN)
            A.setX(x)
            A.setY(pixel_y(Y_NLEN-i))
            B.setY(y)
            x = pixel_x(i+1)
            B.setX(pixel_x(i))
            canvas.drawLine(A, B)
