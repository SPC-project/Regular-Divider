from PyQt5.QtCore import Qt, QPoint


class Rectangle:
    """
    Primitive figure
    """
    def __init__(self, fig, nodes_x, nodes_y):
        self.x, self.y, self.width, self.height = fig
        self.nodes_x = nodes_x
        self.nodes_y = nodes_y

        NA_left, Nx, _ = nodes_x
        NA_top, Ny, _ = nodes_y
        self.step_x = self.width/(Nx-1)  # -1 because N dots cut N-1 segments
        self.step_y = self.height/(Ny-1)
        self.start_x = self.x - self.step_x*NA_left  # where air start
        self.start_y = self.y - self.step_y*NA_top

    def draw(self, canvas, mesh_canvas, shift_x, shift_y, kx, ky):
        def pixel_x(nodes):
            val = shift_x + self.start_x + nodes*self.step_x
            return int(val*kx)

        def pixel_y(nodes):
            val = shift_y + self.start_y + nodes*self.step_y
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
        Xs = self.nodes_x
        Ys = self.nodes_y
        X_NLEN = Xs[0] + Xs[1] + Xs[2]
        Y_NLEN = Ys[0] + Ys[1] + Ys[2]
        X_AIR2 = Xs[0] + Xs[1]  # start of right air layer
        Y_AIR2 = Ys[0] + Ys[1]  # start of bottom air layer
        COL_AIR = Qt.blue
        COL_FIG = Qt.green
        A = QPoint()
        B = QPoint()

        # Horizontal lines
        x0 = pixel_x(0)
        x1 = pixel_x(Xs[0])
        x2 = pixel_x(X_AIR2-1)
        x3 = pixel_x(X_NLEN-1)
        for j in range(Y_NLEN):
            y = pixel_y(j)
            A.setY(y)
            B.setY(y)
            B.setX(x0)
            for xi in (x1, x2, x3):
                A.setX(B.x())
                B.setX(xi)
                if xi == x2 and j >= Ys[0] and j < Y_AIR2:
                    canvas.setPen(COL_FIG)
                else:
                    canvas.setPen(COL_AIR)
                canvas.drawLine(A, B)

        # Vertical lines
        y0 = pixel_y(0)
        y1 = pixel_y(Ys[0])
        y2 = pixel_y(Y_AIR2-1)
        y3 = pixel_y(Y_NLEN-1)
        for i in range(X_NLEN):
            x = pixel_x(i)
            A.setX(x)
            B.setX(x)
            B.setY(y0)
            for yi in (y1, y2, y3):
                A.setY(B.y())
                B.setY(yi)
                if yi == y2 and i >= Xs[0] and i < X_AIR2:
                    canvas.setPen(COL_FIG)
                else:
                    canvas.setPen(COL_AIR)
                canvas.drawLine(A, B)

        # Diagonal lines
        for i in range(X_NLEN - 1):
            x = pixel_x(i)
            y = pixel_y(0)
            B.setY(y)
            A.setX(x)
            for j in range(Y_NLEN - 1):
                if i < Xs[0] or i > X_AIR2-2 or j < Ys[0] or j > Y_AIR2-2:
                    canvas.setPen(COL_AIR)
                else:
                    canvas.setPen(COL_FIG)
                A.setY(B.y())
                x = pixel_x(i+1)
                y = pixel_y(j+1)
                B.setX(x)
                B.setY(y)
                canvas.drawLine(A, B)

    def save(self):
        Xs = self.nodes_x
        Ys = self.nodes_y
        X_NLEN = Xs[0] + Xs[1] + Xs[2]
        Y_NLEN = Ys[0] + Ys[1] + Ys[2]
        X_AIR2 = Xs[0] + Xs[1]  # start of right air layer
        Y_AIR2 = Ys[0] + Ys[1]  # start of bottom air layer

        f = open('temp.pmd', 'w')
        f.write("[settings]\n")
        f.write("n_nodes={}\n".format(X_NLEN*Y_NLEN))
        f.write("n_elements={}\n".format((X_NLEN-1)*(Y_NLEN-1)*2))
        f.write("n_forces=0\n")
        f.write("n_contacts=0\n")

        f.write("[inds]\n")
        for j in range(Y_NLEN-1):
            for i in range(X_NLEN-1):
                # Node's indexing start from 1
                first_ind = i + j*X_NLEN + 1
                second_ind = (i+1) + j*X_NLEN + 1
                third_ind = (i+1) + (j+1)*X_NLEN + 1
                forth_ind = i + (j+1)*X_NLEN + 1
                f.write("{} {} {}\n".format(first_ind, second_ind, third_ind))
                f.write("{} {} {}\n".format(first_ind, third_ind, forth_ind))

        f.write("[koor]\n")
        for i in range(X_NLEN):
            x = i*self.step_x
            for j in range(Y_NLEN):
                y = j*self.step_y
                f.write("{} {}\n".format(x, y))

        f.write("[contact]\n")
        f.write("[force]\n")

        f.write("[material]\n")
        for j in range(Y_NLEN):
            in_figure_y = j >= Ys[0] and j < Y_AIR2
            for i in range(X_NLEN):
                in_figure_x = i >= Xs[0] and i < X_AIR2
                if in_figure_x and in_figure_y:
                    f.write("1\n")  # Figure's flag
                else:
                    f.write("0\n")  # Air

        f.close()
