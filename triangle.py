from primitive import AbstractPrimitive
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPolygon, QBrush
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

    def update_me(self):
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

        for i in range(4):
            if self.binds[i]:
                self.mesh.set_val_at(i, 0)

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
        """
        Divide figure and it's air-rectangles by right triangles
        """
        M = self.mesh
        # Make a rectangle with one diagonal (upper-left bottom-right)
        tile_w = self.step_x * self.drawing_coefs['kx']
        tile_h = self.step_y * self.drawing_coefs['ky']

        # Draw air (draw rectangle tile_w*tile_h and split it by diagonal)
        # Triangle has some at top/bottom (vertical) or left/right (horizontal)
        form = self.mesh.data["form"]
        canvas.setPen(self.COL_AIR)
        horizontal, hor_x = (M.NAL, 0) if form % 2 == 0 else (M.NAR, M.NFX)
        vertical, vert_y = (M.NAT, 0) if form > 1 else (M.NAB, M.NFY)
        if horizontal != 0:
            x, y, w, h = hor_x, 0, horizontal, M.NAT + M.NFY + M.NAB
            self.draw_rect_mesh(canvas, tile_w, tile_h, x, y, w, h)
        if vertical != 0:
            x, y, w, h = M.NAL, vert_y, M.NFX, vertical
            self.draw_rect_mesh(canvas, tile_w, tile_h, x, y, w, h)

        # Draw the figure
        canvas.setPen(self.COL_FIG)
        self.draw_figure_mesh(canvas, tile_w, tile_h, form)

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

    def draw_figure_mesh(self, canvas, tile_w, tile_h, form):
        """
        Divide this triangle by right triangles (legs: tile_w, tile_h)
        If it itself right - it was fully covered by them
        If not - need irregular triangles to cover residual free space
        """
        M = self.mesh

        if self.width == self.height:  # no need in irregular elements
            x, modx = M.NAL, 1
            if form % 2 != 0:
                x, modx = M.NFX - 1, -1
            y, mody = M.NAT, 0
            if form < 2:
                y, mody = M.NAT + 1, 1
            w, h = 1, M.NFY - 1
            for i in range(M.NFX-1):
                self.draw_rect_mesh(canvas, tile_w, tile_h,
                                    x+i*modx, y+i*mody, w, h - i)
        else:  # See explanation in 'doc/triangle draw_mesh.png'
            # NY, NX - how many rectangles we can draw in the triangle
            available_h = self.height - self.height*self.step_x / self.width
            NY = math.floor(available_h / self.step_y)
            tg_alpha = self.width / self.height
            curr_w, curr_h = self.width, self.height
            for j in range(NY):
                available_w = curr_w - curr_w*self.step_y / curr_h
                NX = math.floor(available_w / self.step_x)
                w, h = NX, 1
                x, modx = M.NAL, 1
                if form % 2 != 0:
                    x, modx = M.NFX - NX, -1
                y, mody = M.NAT + j, 0
                if form < 2:
                    y, mody = M.NFY - 1 - j, 1

                self.draw_rect_mesh(canvas, tile_w, tile_h, x, y, w, h)
                curr_h -= self.step_y
                curr_w = curr_h * tg_alpha
