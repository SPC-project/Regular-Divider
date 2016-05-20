from PyQt5.QtCore import Qt, QPoint


class Rectangle:
    """
    Primitive figure
    """
    def __init__(self, x, y, width, height, Nx, Ny):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.Nx = Nx
        self.Ny = Ny

    def draw(self, canvas, shift_x, shift_y, kx, ky):
        canvas.setPen(Qt.black)
        canvas.drawRect(int((shift_x + self.x)*kx), int((shift_y + self.y)*ky),
                        int(self.width*kx), int(self.height*ky))


class Mesh_rectangle:
    """
    Rectangle meshed by triangles
    """
    def __init__(self, x, y, dx, dy, Nx, Ny, NAtop, NAright, NAbottom, NAleft):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.nodes_x = (NAleft, Nx, NAright)
        self.nodes_y = (NAtop, Ny, NAbottom)

    def draw(self, canvas, shift_x, shift_y, kx, ky):
        Xs = self.nodes_x
        Ys = self.nodes_y
        X_NLEN = Xs[0] + Xs[1] + Xs[2]
        Y_NLEN = Ys[0] + Ys[1] + Ys[2]
        X_AIR2 = Xs[0] + Xs[1] - 1  # start of right air layer
        Y_AIR2 = Ys[0] + Ys[1] - 1  # start of bottom air layer
        COL_AIR = Qt.blue
        COL_FIG = Qt.green

        A = QPoint()
        B = QPoint()
        # Horizontal lines
        for j in range(Y_NLEN):
            x = int((shift_x + self.x)*kx)
            y = int((shift_y + self.y + j*self.dy)*ky)
            B.setX(x)
            B.setY(y)
            A.setY(y)
            for i in range(X_NLEN - 1):
                if i < Xs[0] or i >= X_AIR2 or j < Ys[0] or j > Y_AIR2:
                    canvas.setPen(COL_AIR)
                else:
                    canvas.setPen(COL_FIG)
                A.setX(B.x())
                x = int((shift_x + self.x + (i+1)*self.dx)*kx)
                B.setX(x)
                canvas.drawLine(A, B)

        # Vertical lines
        for i in range(X_NLEN):
            x = int((shift_x + self.x + i*self.dx) * kx)
            y = int((shift_y + self.y)*ky)
            B.setX(x)
            B.setY(y)
            A.setX(x)
            for j in range(Y_NLEN - 1):
                if i < Xs[0] or i > X_AIR2 or j < Ys[0] or j >= Y_AIR2:
                    canvas.setPen(COL_AIR)
                else:
                    canvas.setPen(COL_FIG)
                A.setY(B.y())
                y = int((shift_y + self.y + (j+1)*self.dy)*ky)
                B.setY(y)
                canvas.drawLine(A, B)

        # Diagonal lines
        for i in range(X_NLEN - 1):
            x = int((shift_x + self.x + i*self.dx) * kx)
            y = int((shift_y + self.y)*ky)
            B.setY(y)
            A.setX(x)
            for j in range(Y_NLEN - 1):
                if i < Xs[0] or i >= X_AIR2 or j < Ys[0] or j >= Y_AIR2:
                    canvas.setPen(COL_AIR)
                else:
                    canvas.setPen(COL_FIG)
                A.setY(B.y())
                x = int((shift_x + self.x + (i+1)*self.dx)*kx)
                y = int((shift_y + self.y + (j+1)*self.dy)*ky)
                B.setX(x)
                B.setY(y)
                canvas.drawLine(A, B)
