import unittest

from src.gui_primitive import NewRectangleWidget
from src.figure import Figure, Output
from src.primitive import Mesh


class FakeParentApp:
    def setText(self, txt):
        pass

    def adjustSize(self):
        pass

    def emit(self):
        pass


class AbstractTest(unittest.TestCase):
    def setUp(self):
        holder = FakeParentApp()
        self.fig = Figure(holder, holder, holder, holder)
        self.fig.world_size = 10
        self.fig.start_x = 0
        self.fig.start_y = 0

    def get_rectangle(self, nx, ny, top=0, right=0, bottom=0, left=0):
        box = (left, top, nx-1, ny-1)  # x, y, w, h

        # Во внутреннем представлении используются квадраты, а не узлы
        nodes = [top, right, bottom, left, nx-1, ny-1]

        other_data = {'type': 'rectangle'}
        mesh = Mesh(nodes, other_data)

        return box, mesh, 0  # '0' for Rectangle

    def get_triangle(self, form, nx=2, ny=2, horizontal=0, vertical=0, x0=0.0, y0=0.0):
        box = (x0, y0, nx-1, ny-1)  # x, y, w, h
        if form == 0:
            # air: top, right, bottom, left; figure 'squares': by x, by y
            # see gui_primitive.py for details
            nodes = [0, 0, horizontal, vertical, nx-1, ny-1]
        elif form == 1:
            nodes = [0, vertical, horizontal, 0, nx-1, ny-1]
        elif form == 2:
            nodes = [horizontal, 0, 0, vertical, nx-1, ny-1]
        elif form == 3:
            nodes = [horizontal, vertical, 0, 0, nx-1, ny-1]

        other_data = {'type': 'triangle', 'form': form}
        mesh = Mesh(nodes, other_data)

        return box, mesh, 1  # '1' for Triangle

    def check_mesh(self, input, elems_test, coords_test, name):
        """
        elements_test — список элементов, что будут образованы разбиением. Элемент задается индексами трёх формирующих его вершин
        coords_test — список координат узлов. Индекс узла указан третьим числом в строке
        """
        self.fig.adopt_primitive(*input)
        self.fig.save_mesh()

        self.check_output(elems_test, coords_test, name)

    def check_output(self, elems_test, coords_test):
        with open(Output.TEMP_DIR + Output.FILENAMES[0] + ".tmp", "r") as f:
            triangles = f.readlines()
            self.assertEqual(triangles, elems_test, "Wrong triangles formed for")

        with open(Output.TEMP_DIR + Output.FILENAMES[1] + ".tmp", "r") as f:
            coords = [[float(elem) for elem in line.split(' ')] for line in f.readlines()]  # convert lines to Python's list[list]
            counter = 0
            for line in coords:
                self.assertEqual(line[2], counter, "Numeration break")
                del line[2]
                counter += 1
            self.assertEqual(coords, coords_test, "Wrong coordinates")
