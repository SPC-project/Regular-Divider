from PyQt5.QtCore import Qt, QPoint

NAT = 0
NAR = 1
NAB = 2
NAL = 3
NX = 4
NY = 5


class Rectangle:
    """
    Primitive figure, a rectangle
    """
    def __init__(self, fig, mesh):
        """
        fig: tuple of rectangle - (x, y, width, hegiht)
        mesh: specify how to divide @fig, list - [NAT, NAR, NAB, NAL, NX, NY]
            NAT - how many air elements at the top of @fig
            NAR - air elements at right
            NAB - air elements at bottom
            NAL - air elements at left
            NX - count of fig's elements by width
            NY - count of fig's elements by height
        """
        self.binds = [False]*4
        self.modify(fig, mesh)

    def modify(self, fig, mesh):
        self.x, self.y, self.width, self.height = fig
        self.mesh = mesh

        # if has connection to another Rectangles, 'shave' that edge from air
        for i in range(4):
            if self.binds[i]:
                self.mesh[i] = 0

        self.step_x = self.width/mesh[NX]
        self.step_y = self.height/mesh[NY]
        self.start_x = self.x - self.step_x*mesh[NAL]  # where air start
        self.start_y = self.y - self.step_y*mesh[NAT]

    def shave_air(self, edge):
        self.binds[edge] = True
        fig = (self.x, self.y, self.width, self.height)
        self.modify(fig, self.mesh)

    def draw(self, canvas, mesh_canvas, shift_x, shift_y, kx, ky):
        def pixel_x(n_elements):
            val = shift_x + self.start_x + n_elements*self.step_x
            return int(val*kx)

        def pixel_y(n_elements):
            val = shift_y + self.start_y + n_elements*self.step_y
            return int(val*ky)

        self.draw_figure(canvas, shift_x, shift_y, kx, ky)
        self.draw_mesh(mesh_canvas, pixel_x, pixel_y)

    def draw_figure(self, canvas, shift_x, shift_y, kx, ky):
        canvas.setPen(Qt.black)
        x = int((shift_x + self.x)*kx)
        y = int((shift_y + self.y)*ky)
        w = int(self.width*kx)
        h = int(self.height*ky)
        canvas.drawRect(x, y, w, h)

    def draw_mesh(self, canvas, pixel_x, pixel_y):
        """
        Split rectangle to smaller rectangles step_x*step_y,
        then for each draw diagonal
        """
        M = self.mesh
        X1 = M[NAL]
        Y1 = M[NAT]
        X2 = M[NAL] + M[NX]  # start of right air layer
        Y2 = M[NAT] + M[NY]  # start of bottom air layer
        X_NLEN = X2 + M[NAR]
        Y_NLEN = Y2 + M[NAB]
        COL_AIR = Qt.blue
        COL_FIG = Qt.green
        A = QPoint()
        B = QPoint()

        # Horizontal lines (3 segments: air, figure, air)
        x0 = pixel_x(0)
        x1 = pixel_x(X1)
        x2 = pixel_x(X2)
        x3 = pixel_x(X_NLEN)
        for j in range(Y_NLEN+1):  # +1 because N segments defined by N+1 dots
            y = pixel_y(j)
            A.setY(y)
            B.setY(y)
            B.setX(x0)
            for xi in (x1, x2, x3):
                A.setX(B.x())
                B.setX(xi)
                if xi == x2 and j >= Y1 and j <= Y2:
                    canvas.setPen(COL_FIG)
                else:
                    canvas.setPen(COL_AIR)
                canvas.drawLine(A, B)

        # Vertical lines
        y0 = pixel_y(0)
        y1 = pixel_y(Y1)
        y2 = pixel_y(Y2)
        y3 = pixel_y(Y_NLEN)
        for i in range(X_NLEN+1):
            x = pixel_x(i)
            A.setX(x)
            B.setX(x)
            B.setY(y0)
            for yi in (y1, y2, y3):
                A.setY(B.y())
                B.setY(yi)
                if yi == y2 and i >= X1 and i <= X2:
                    canvas.setPen(COL_FIG)
                else:
                    canvas.setPen(COL_AIR)
                canvas.drawLine(A, B)

        # Diagonal lines
        for i in range(X_NLEN):  # no need +1: one diagonal for every rectangle
            x = pixel_x(i)
            y = pixel_y(0)
            B.setY(y)
            A.setX(x)
            for j in range(Y_NLEN):
                if X1 <= i and i < X2 and Y1 <= j and j < Y2:
                    canvas.setPen(COL_FIG)
                else:
                    canvas.setPen(COL_AIR)
                A.setY(B.y())
                x = pixel_x(i+1)
                y = pixel_y(j+1)
                B.setX(x)
                B.setY(y)
                canvas.drawLine(A, B)

    def save(self):
        M = self.mesh
        X1 = M[NAL]
        Y1 = M[NAT]
        X2 = X1 + M[NX]  # start of right air layer
        Y2 = Y1 + M[NY]  # start of bottom air layer
        X_NLEN = X2 + M[NAR]
        Y_NLEN = Y2 + M[NAB]
        XNODES = X_NLEN + 1
        YNODES = Y_NLEN + 1

        f = open('temp.pmd', 'w')
        f.write("[settings]\n")
        f.write("n_nodes={}\n".format(XNODES*YNODES))
        f.write("n_elements={}\n".format(X_NLEN*Y_NLEN*2))
        f.write("n_forces=0\n")
        f.write("n_contacts=0\n")

        f.write("[inds]\n")
        for j in range(Y_NLEN):
            for i in range(X_NLEN):
                # +1 because node indexing start from 1, not 0
                first_ind = i + j*XNODES + 1
                second_ind = (i+1) + j*XNODES + 1
                third_ind = (i+1) + (j+1)*XNODES + 1
                forth_ind = i + (j+1)*XNODES + 1
                f.write("{} {} {}\n".format(first_ind, second_ind, third_ind))
                f.write("{} {} {}\n".format(first_ind, third_ind, forth_ind))

        f.write("[koor]\n")
        for i in range(XNODES):
            x = i*self.step_x
            for j in range(YNODES):
                y = j*self.step_y
                f.write("{} {}\n".format(x, y))

        f.write("[contact]\n")
        f.write("[force]\n")

        f.write("[material]\n")
        for j in range(YNODES):
            in_figure_y = j >= Y1 and j <= Y2
            for i in range(XNODES):
                in_figure_x = i >= X1 and i <= X2
                if in_figure_x and in_figure_y:
                    f.write("1\n")  # Figure's flag
                else:
                    f.write("0\n")  # Air

        f.write("[material for elements]\n")
        for j in range(Y_NLEN):
            in_figure_y = j >= Y1 and j < Y2
            for i in range(X_NLEN):
                in_figure_x = i >= X1 and i < X2
                if in_figure_x and in_figure_y:
                    f.write("1\n")  # Figure's flag
                    f.write("1\n")  # Figure's flag
                else:
                    f.write("0\n")  # Air
                    f.write("0\n")  # Air
        f.close()
