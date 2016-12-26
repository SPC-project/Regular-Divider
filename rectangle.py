from PyQt5.QtCore import QPoint, QRect
from primitive import AbstractPrimitive

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
        # if has connection to another Rectangles, 'shave' that edge from air
        for i in range(4):
            if self.binds[i]:
                self.mesh.set_val_at(i, 0)

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

    def save_indexes(self, f, index_start):
        x_elem = self.element_count_w - 1
        y_elem = self.element_count_h - 1
        x_nodes = self.element_count_w
        y_nodes = self.element_count_h
        # N отрезков создаются N+1 точками - будем добавлять 1 в конце цепочки
        if not self.binds[air_nodes_right]:
            x_nodes += 1
            x_elem += 1
        if not self.binds[air_nodes_bottom]:
            y_nodes += 1
            y_elem += 1

        self.index_start = index_start
        self.problem_zone_first_index = self.index_start + x_nodes*y_nodes

        # Divide self to rectangular grid and split every rectangle by diagonal
        for j in range(y_elem):
            for i in range(x_elem):
                # +1 because node indexing start from 1, not 0
                first_ind = index_start + i + j*x_nodes + 1
                second_ind = index_start + (i+1) + j*x_nodes + 1
                third_ind = index_start + (i+1) + (j+1)*x_nodes + 1
                forth_ind = index_start + i + (j+1)*x_nodes + 1
                f.write("{} {} {}\n".format(first_ind, second_ind, third_ind))
                f.write("{} {} {}\n".format(first_ind, third_ind, forth_ind))

        return self.problem_zone_first_index

    def deal_with_horizontal_contact_regions(self, f, index, sewing_nodes, material):
        if not self.binds[air_nodes_top]:
            return index

        he = self.binds[air_nodes_right]
        dy = self.step_y  # step_y should be same
        end_self = self.start_y + self.element_count_h * dy
        end_he = he.start_y + he.element_count_h * dy

        W_self = self.element_count_w  # here element_count_w fine
        W_he = he.element_count_w + 1  # need nodes_count_w, actually
        SEW_X = self.start_x + W_self*self.step_x
        fig_start_self = self.start_y + self.mesh.NAT*dy
        fig_end_self = fig_start_self + self.mesh.NFY*dy
        fig_start_he = he.start_y + he.mesh.NAT*dy
        fig_end_he = fig_start_he + he.mesh.NFY*dy

        iterate_count = int((end_self-self.start_y) / dy)
        offset_he = int((he.start_y - self.start_y) / dy)
        created = False
        added1 = False
        left1_is_air = True
        left2_is_air = True
        right1_is_air = True
        right2_is_air = True
        for j in range(iterate_count):
            left1_is_air = True
            left2_is_air = True
            right1_is_air = True
            right2_is_air = True
            pos = self.start_y + j*dy
            left_node_1 = self.index_start + (j+1)*W_self  # TODO be wise rename step_y to dy (misspell with start_y)
            left_node_2 = self.index_start + (j+2)*W_self

            if fig_start_self <= pos and pos <= fig_end_self:
                left1_is_air = False
            if fig_start_self <= pos+dy and pos+dy <= fig_end_self:
                left2_is_air = False

            if he.start_y <= pos and pos <= end_he:
                right_node_1 = he.index_start + (j-offset_he)*W_he + 1
                if fig_start_he <= pos and pos <= fig_end_he:
                    right1_is_air = False
            else:
                index += 1
                right_node_1 = index
                new_node = (index, SEW_X, pos)
                sewing_nodes.append(new_node)
                created = False
                added1 = True

            if he.start_y <= pos+dy and pos+dy <= end_he:
                right_node_2 = he.index_start + (j-offset_he+1)*W_he + 1
                if fig_start_he <= pos+dy and pos+dy <= fig_end_he:
                    right2_is_air = False
            else:
                right_node_2 = index + 1
                new_node = (index+1, SEW_X, pos+dy)
                created = True
                sewing_nodes.append(new_node)

            f.write("{} {} {}\n".format(left_node_1, right_node_1, right_node_2))

            if added1:
                added1 = False
                if left1_is_air and right1_is_air:
                    material.append(0)
                else:
                    material.append(1)
            f.write("{} {} {}\n".format(left_node_1, left_node_2, right_node_2))

        if created:
            index += 1
            if left2_is_air and right2_is_air:
                material.append(0)
            else:
                material.append(1)

        return index

    def deal_with_vertical_contact_regions(self, f, index, sewing_nodes, material):
        if not self.binds[air_nodes_bottom]:
            return index

        he = self.binds[air_nodes_bottom]
        dx = self.step_x  # step_y should be same
        end_he = he.start_x + he.element_count_w * dx

        fig_start_self = self.start_x + self.mesh.NAL*dx
        fig_end_self = fig_start_self + self.mesh.NAT*dx
        fig_start_he = he.start_x + he.mesh.NAL*dx
        fig_end_he = fig_start_he + he.mesh.NAT*dx

        SEW_Y = self.start_y + self.element_count_h*self.step_y
        offset_self = (self.element_count_w+1)*(self.element_count_h-1)
        offset_he = int((he.start_x - self.start_x) / dx)
        created = False
        added1 = False
        left1_is_air = True
        left2_is_air = True
        right1_is_air = True
        right2_is_air = True
        for i in range(self.element_count_w):
            pos = self.start_x + i*dx
            left_node_1 = self.index_start + offset_self + i + 1
            left_node_2 = self.index_start + offset_self + i+2
            left1_is_air = True
            left2_is_air = True
            right1_is_air = True
            right2_is_air = True
            if fig_start_self <= pos and pos <= fig_end_self:
                left1_is_air = False
            if fig_start_self <= pos+dx and pos+dx <= fig_end_self:
                left2_is_air = False

            if he.start_x <= pos and pos <= end_he:
                right_node_1 = he.index_start + i-offset_he + 1
                if fig_start_he <= pos and pos <= fig_end_he:
                    right1_is_air = False
            else:
                index += 1
                right_node_1 = index
                new_node = (index, pos, SEW_Y)
                sewing_nodes.append(new_node)
                created = False
                added1 = True

            if he.start_x <= pos+dx and pos+dx <= end_he:
                right_node_2 = he.index_start + i-offset_he+1 + 1
                if fig_start_he <= pos+dx and pos+dx <= fig_end_he:
                    right2_is_air = False
            else:
                right_node_2 = index + 1
                new_node = (index+1, pos+dx, SEW_Y)
                sewing_nodes.append(new_node)
                created = True

            f.write("{} {} {}\n".format(left_node_1, right_node_1, right_node_2))
            if added1:
                added1 = False
                if left1_is_air and right1_is_air:
                    material.append(0)
                else:
                    material.append(1)
            f.write("{} {} {}\n".format(left_node_1, left_node_2, right_node_2))

        if created:
            index += 1
            if left2_is_air and right2_is_air:
                material.append(0)
            else:
                material.append(1)

        return index

    def save_coor(self, f):
        x_nodes = self.element_count_w
        y_nodes = self.element_count_h
        # N отрезков создаются N+1 точками - будем добавлять 1 в конце цепочки
        if not self.binds[air_nodes_right]:
            x_nodes += 1
        if not self.binds[air_nodes_bottom]:
            y_nodes += 1
        for j in range(y_nodes):
            y = self.start_y + j*self.step_y
            for i in range(x_nodes):
                x = self.start_x + i*self.step_x
                f.write("{} {}\n".format(x, y))

    def save_material(self, f):
        x_nodes = self.element_count_w
        y_nodes = self.element_count_h
        if not self.binds[air_nodes_right]:
            x_nodes += 1
        if not self.binds[air_nodes_bottom]:
            y_nodes += 1
        M = self.mesh
        X1 = M.NAL
        Y1 = M.NAT
        X2 = X1 + M.NFX  # start of right air layer
        Y2 = Y1 + M.NFY  # start of bottom air layer

        for j in range(y_nodes):
            in_figure_y = j >= Y1 and j <= Y2
            for i in range(x_nodes):
                in_figure_x = i >= X1 and i <= X2
                if in_figure_x and in_figure_y:
                    f.write("1\n")  # Figure's flag
                else:
                    f.write("0\n")  # Air

    def save_material_of_element(self, f):
        M = self.mesh
        X1 = M.NAL
        Y1 = M.NAT
        X2 = X1 + M.NFX  # start of right air layer
        Y2 = Y1 + M.NFY  # start of bottom air layer
        for j in range(self.element_count_h):
            in_figure_y = j >= Y1 and j < Y2
            for i in range(self.element_count_w):
                in_figure_x = i >= X1 and i < X2
                if in_figure_x and in_figure_y:
                    f.write("1\n")  # Figure's flag
                    f.write("1\n")  # Figure's flag
                else:
                    f.write("0\n")  # Air
                    f.write("0\n")  # Air
