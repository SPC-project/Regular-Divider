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

    def draw(self, canvas, kx, ky):
        canvas.setPen(Qt.black)
        canvas.drawRect(int(self.x*kx), int(self.y*ky),
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

    def draw(self, canvas, kx, ky):
        Xs = self.nodes_x
        Ys = self.nodes_y

        canvas.setPen(Qt.blue)
        A = QPoint()
        B = QPoint()
        # Horizontal lines
        for j in range(Ys[0] + Ys[1] + Ys[2]):
            x = int(self.x*kx)
            y = int((self.y + j*self.dy)*ky)
            B.setX(x)
            B.setY(y)
            A.setY(y)
            for i in range(Xs[0] + Xs[1] + Xs[2] - 1):
                A.setX(B.x())
                x = int((self.x + (i+1)*self.dx)*kx)
                B.setX(x)
                canvas.drawLine(A, B)

        # Vertical lines
        for i in range(Xs[0] + Xs[1] + Xs[2]):
            x = int((self.x + i*self.dx) * kx)
            y = int(self.y*ky)
            B.setX(x)
            B.setY(y)
            A.setX(x)
            for j in range(Ys[0] + Ys[1] + Ys[2] - 1):
                A.setY(B.y())
                y = int((self.y + (j+1)*self.dy)*ky)
                B.setY(y)
                canvas.drawLine(A, B)

