from PyQt5.QtCore import QPoint, QRect
from src.primitive import AbstractPrimitive

air_nodes_top = 0
air_nodes_right = 1
air_nodes_bottom = 2


class Rectangle(AbstractPrimitive):
    """
    Primitive figure, a rectangle
    """
    def __init__(self, fig, mesh):
        """
        fig: tuple of rectangle - (x, y, width, height)
        mesh: class specified at primitive_dialogues.py
            mesh.NAT - how many air elements at the top of @fig
            mesh.NAR - air elements at right
            mesh.NAB - air elements at bottom
            mesh.NAL - air elements at left
            mesh.NFX - count of fig's elements by width
            mesh.NFY - count of fig's elements by height
        """
        self.binds = [None]*4
        super(Rectangle, self).__init__(fig, mesh)

    def update_me(self):
        pass

    def draw_figure(self, canvas):
        canvas.setPen(self.COL_FIG)
        x = self.scale_x(self.x)
        y = self.scale_y(self.y)
        w = int(round(self.width*self.drawing_coefs['kx']))
        h = int(round(self.height*self.drawing_coefs['kx']))
        canvas.drawRect(x, y, w, h)

    def draw_mesh(self, canvas):
        """
        Split rectangle to smaller rectangles step_x*step_y,
        then for each draw diagonal
        """
        M = self.mesh
        X1 = M.NAL  # start of figure
        Y1 = M.NAT  # start of figure
        X2 = M.NAL + M.NFX  # start of right air layer
        Y2 = M.NAT + M.NFY  # start of bottom air layer
        X_NLEN = X2 + M.NAR
        Y_NLEN = Y2 + M.NAB
        A = QPoint()
        B = QPoint()

        # Horizontal lines (3 segments: air, figure, air)
        x0 = self.pixel_x(0)
        x1 = self.pixel_x(X1)
        x2 = self.pixel_x(X2)
        x3 = self.pixel_x(X_NLEN)
        for j in range(Y_NLEN+1):  # +1 because N segments defined by N+1 dots
            y = self.pixel_y(j)
            A.setY(y)
            B.setY(y)
            B.setX(x0)
            for xi in (x1, x2, x3):
                A.setX(B.x())
                B.setX(xi)
                if xi == x2 and j >= Y1 and j <= Y2:
                    canvas.setPen(self.COL_FIG)
                else:
                    canvas.setPen(self.COL_AIR)
                canvas.drawLine(A, B)

        # Vertical lines
        y0 = self.pixel_y(0)
        y1 = self.pixel_y(Y1)
        y2 = self.pixel_y(Y2)
        y3 = self.pixel_y(Y_NLEN)
        for i in range(X_NLEN+1):
            x = self.pixel_x(i)
            A.setX(x)
            B.setX(x)
            B.setY(y0)
            for yi in (y1, y2, y3):
                A.setY(B.y())
                B.setY(yi)
                if yi == y2 and i >= X1 and i <= X2:
                    canvas.setPen(self.COL_FIG)
                else:
                    canvas.setPen(self.COL_AIR)
                canvas.drawLine(A, B)

        # Diagonal lines
        for i in range(X_NLEN):  # no need +1: one diagonal for every rectangle
            x = self.pixel_x(i)
            y = self.pixel_y(0)
            B.setY(y)
            A.setX(x)
            for j in range(Y_NLEN):
                A.setY(B.y())
                x = self.pixel_x(i+1)
                y = self.pixel_y(j+1)
                B.setX(x)
                B.setY(y)
                if X1 <= i and i < X2 and Y1 <= j and j < Y2:
                    canvas.setPen(self.COL_FIG)
                else:
                    canvas.setPen(self.COL_AIR)
                canvas.drawLine(A, B)

        # Fill the figure
        A.setX(self.pixel_x(X1))
        A.setY(self.pixel_y(Y1))
        B.setX(self.pixel_x(X2))
        B.setY(self.pixel_y(Y2))
        canvas.fillRect(QRect(A, B), self.COL_FIG_INNNER)

    def save_mesh(self, output):
        """
        See primitive.py/AbstractPrimitive/save_mesh for description
        index — индекс, с которого начнём нумерацию узлов
        """
        M = self.mesh
        width_height = [
            [M.NAL + M.NFX + M.NAR, M.NAT],
            [M.NAL, M.NFY],
            [M.NAL + M.NFX + M.NAR, M.NAB],
            [M.NAR, M.NFY],
            [M.NFX, M.NFY]
        ]

        x0, y0 = self.start_x, self.start_y
        dx, dy = self.step_x, self.step_y
        x_y = [
            [x0, y0],
            [x0, y0 + M.NAT*dy],
            [x0, y0 + (M.NAT+M.NFY)*dy],
            [x0 + (M.NAL+M.NFX)*dx, y0 + M.NAT*dy],
            [x0 + M.NAL*dx, y0 + M.NAT*dy]
        ]

        air = self.AIR_CODE
        fig = self.FIGURE_CODE
        material = [air, air, air, air, fig]

        for i in range(5):
            w, h = width_height[i]
            if w == 0 or h == 0:
                continue
            x, y = x_y[i]
            mtrl = material[i]
            self.save_rectangle_mesh(w, h, output, x, y, dx, dy, mtrl)
