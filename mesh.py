from primitives import Mesh_rectangle


class Mesh:
    def __init__(self):
        self.shape = list()
        pass

    def add(self, rect, Nx, Ny, NAtop, NAright, NAbottom, NAleft):
        """
        Add new mesh

        Args:
            rect: x, y, width, height
            Nx, Ny: number of nodes per x/y axis
            NA*: number of air nodes
        """
        step_x = rect.width/(Nx-1)  # -1 because N dots produce N-1 segments
        step_y = rect.height/(Ny-1)
        start_x = rect.x - step_x*NAright
        start_y = rect.y - step_y*NAtop
        mr = Mesh_rectangle(start_x, start_y, step_x, step_y,
                            Nx, Ny, NAtop, NAright, NAbottom, NAleft)
        self.shape.append(mr)

    def redraw(self, canvas, shift_x, shift_y, kx, ky):
        for primitive in self.shape:
            primitive.draw(canvas, shift_x, shift_y, kx, ky)
