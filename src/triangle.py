from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPolygon, QBrush
import math
from src.primitive import AbstractPrimitive


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

        # Triangle has some air at top/bottom (horizontal) or left/right (vertical)
        form = self.mesh.data["form"]
        canvas.setPen(self.COL_AIR)
        sides, side_x = (M.NAL, 0) if form % 2 == 0 else (M.NAR, M.NFX)
        botop, botop_y = (M.NAT, 0) if form > 1 else (M.NAB, M.NFY)
        if sides != 0:
            x, y, w, h = side_x, 0, sides, M.NAT + M.NFY + M.NAB
            self.draw_rect_mesh(canvas, tile_w, tile_h, x, y, w, h)
        if botop != 0:
            x, y, w, h = M.NAL, botop_y, M.NFX, botop
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

    def save_mesh(self, output):
        """
         Каждый вызов save_rectangle_mesh начинает нумерацию с нового индекса, что
        означает появление дублирующих узлов в файлах промежуточного разбиения.
        Это будет улажено позже, вызовом утилиты, что собирает результирующий файл
        """
        M = self.mesh
        form = self.mesh.data["form"]
        dx = self.step_x
        dy = self.step_y

        # Create mesh for air layers: left/right(vertical) and top/bottom (horizontal)
        #  see doc/forms_of_triangles.png for context
        #  Horizontal boxes get excessive corner's part of air layout
        hor_layer_w, hor_offset_nodes = (M.NAL, 0) if form % 2 == 0 else (M.NAR, M.NFX)
        vert_layer_h, vert_offset_nodes = (M.NAT, 0) if form > 1 else (M.NAB, M.NFY)
        if hor_layer_w != 0:
            w, h = hor_layer_w, M.NAT + M.NFY + M.NAB
            x0 = self.start_x + hor_offset_nodes*dx
            y0 = self.start_y
            self.save_rectangle_mesh(w, h, output, x0, y0, dx, dy)
        if vert_layer_h != 0:
            w, h = M.NFX, vert_layer_h
            x0 = self.start_x + M.NAL*dx
            y0 = self.start_y + vert_offset_nodes*dy
            self.save_rectangle_mesh(w, h, output, x0, y0, dx, dy)

        if self.width == self.height:  # no need in irregular elements
            self.save_isosceles_figure_mesh(output, form)
        else:
            self.save_nonisosceles_figure_mesh(output, form)

    def save_isosceles_figure_mesh(self, output, type_):
        """
         Create mesh for isosceles triangle
         Create rectanglar mesh near vertical cathetus
        """
        M = self.mesh
        offset_x, offset_y = 0, 0  # offset in nodes to where start first rectangle
        mod_x, mod_y = 0, 0  # change direction with that
        x0, y0 = self.start_x, self.start_y
        dx, dy = self.step_x, self.step_y
        start = output.last_index

        if type_ == 0:
            offset_x, mod_x = M.NAL, 1
            offset_y, mod_y = 1, 1  # if start at 0, rectangle will penetrate figure's boundaries
            output.save_node(x0 + M.NAL*dx, y0, self.FIGURE_CODE)  # create save_node top-left save_node
        elif type_ == 1:
            offset_x, mod_x = M.NFX-1, -1
            offset_y, mod_y = 1, 1
            output.save_node(x0 + M.NFX*dx, y0, self.FIGURE_CODE)
        elif type_ == 2:
            offset_x, mod_x = M.NAL, 1
            offset_y, mod_y = M.NAT, 0
            # Use 'output.save_node' after create main figure,
            #   hypotenuse is at bottom-right of it
        elif type_ == 3:
            offset_x, mod_x = M.NFX-1, -1
            offset_y, mod_y = M.NAT, 0

        w, h = 1, M.NFY-1  # '-1' or corner of last rectangle will penetrate boundaries of the figure
        for i in range(M.NFX-1):
            x = x0 + (offset_x + mod_x*i)*dx
            y = y0 + (offset_y + mod_y*i)*dy
            self.save_rectangle_mesh(w, h-i, output, x, y, dx, dy)

        if type_ == 0:
            output.save_node(x0 + (M.NAL + M.NFX)*dx, y0 + M.NFY*dy, self.FIGURE_CODE)
            self.fill_gaps_on_type0_hypotenuse(output, start)
        elif type_ == 1:
            output.save_node(x0, y0 + M.NFY*dy, self.FIGURE_CODE)
            self.fill_gaps_on_type1_hypotenuse(output, start)
        if type_ == 2:
            bottom = output.last_index
            output.save_node(x0 + M.NAL*dx, y0 + (M.NAT + M.NFY)*dy, self.FIGURE_CODE)
            output.save_node(x0 + (M.NAL + M.NFX)*dx, y0 + M.NAT*dy, self.FIGURE_CODE)
            self.fill_gaps_on_type2_hypotenuse(output, start, bottom)
        if type_ == 3:
            output.save_node(x0, y0 + M.NAT*dy, self.FIGURE_CODE)
            last = output.last_index
            output.save_node(x0 + M.NFX*dx, y0 + (M.NAT + M.NFY)*dy, self.FIGURE_CODE)
            self.fill_gaps_on_type3_hypotenuse(output, start, last)

    def fill_gaps_on_type0_hypotenuse(self, output, start):
        next_left = start + 1
        next_right = start + 2
        for k in range(self.mesh.NFX, 0, -1):  # fill gaps on hypotenuse
            output.save_element(start, next_left, next_right, self.FIGURE_CODE)
            start = next_right
            next_left = next_right + 2
            next_right = next_right + k*2
            if k == 2:
                next_right -= 1

    def fill_gaps_on_type1_hypotenuse(self, output, start):
        next_right = start + 2
        next_left = start + 1
        for k in range(self.mesh.NFX, 0, -1):  # fill gaps on hypotenuse
            output.save_element(start, next_right, next_left, self.FIGURE_CODE)
            start = next_left
            next_right = next_left + 2
            next_left = next_left + k*2

    def fill_gaps_on_type2_hypotenuse(self, output, start, bottom):
        next_right = start + self.mesh.NFY*2 - 1
        next_left = next_right - 1
        for k in range(self.mesh.NFX, 1, -1):  # fill gaps on hypotenuse
            output.save_element(next_left, bottom, next_right, self.FIGURE_CODE)
            bottom = next_right
            next_right = next_right + (k-1)*2
            next_left = next_right - 1
        next_right = output.last_index - 1
        next_left = output.last_index - 5
        output.save_element(next_left, bottom, next_right, self.FIGURE_CODE)

    def fill_gaps_on_type3_hypotenuse(self, output, start, last):
        left = last - 1  # left vertex of the triangle
        next_up = last - 5  # index of upper-left save_node of created mesh
        next_down = last - 3
        for k in range(self.mesh.NFX, 1, -1):  # fill gaps on hypotenuse
            output.save_element(left, next_up, next_down, self.FIGURE_CODE)
            left = next_down
            next_up = next_down + 1
            next_down = next_down - 4
        left = start + self.mesh.NFY*2 - 2
        next_up = left + 1
        next_down = last
        output.save_element(left, next_up, next_down, self.FIGURE_CODE)

    def save_nonisosceles_figure_mesh(self, output, form):
        # See doc/create_triangle_mesh.png for some explanation
        M = self.mesh

        w, h = self.step_x, self.step_y
        available_w = self.width - self.width * h/self.height
        nodes_by_x = math.floor(available_w / w)
        tg_alpha = self.width / self.height
        curr_w, curr_h = self.width, self.height
        for i in range(nodes_by_x):
            available_h = curr_h - curr_h * w/curr_w
            nodes_by_y = math.floor(available_h / h)
            x0, y0 = 0, 0
            if form % 2 == 0:
                x0 = self.start_x + M.NAL*w
            else:
                x0 = self.start_x + (M.NFX - nodes_by_x)*w
            if form < 2:
                y0 = self.start_y + self.height - available_h
            else:
                y0 = self.start_y + M.NAT*h

            self.save_rectangle_mesh(1, nodes_by_y, output, x0, y0, w, h)
            curr_h = available_h
            curr_w = curr_h * tg_alpha
