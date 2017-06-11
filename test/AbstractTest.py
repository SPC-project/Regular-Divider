import unittest

from src.figure import Figure, Output
from src.primitive import Mesh
import subprocess
import os

OUTPUT_FILENAME = Output.TEMP_DIR + "/test.pmd"
EXPORT_OUTPUT_FILENAME = Output.TEMP_DIR + "/test.d42do"


class FakeParentApp:
    def setText(self, txt):
        pass

    def adjustSize(self):
        pass

    def emit(self):
        pass


class AbstractTest(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(Output.TEMP_DIR):
            os.makedirs(Output.TEMP_DIR)

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

    def get_pos_rectangle(self, x, y, nx, ny, top=0, right=0, bottom=0, left=0):
        box = (x, y, nx-1, ny-1)  # x, y, w, h
        nodes = [top, right, bottom, left, nx-1, ny-1]
        other_data = {'type': 'rectangle'}
        mesh = Mesh(nodes, other_data)

        return box, mesh, 0  # '0' for Rectangle

    def get_triangle(self, form, nx=2, ny=2, top=0, right=0, bottom=0, left=0):
        box = (left, top, nx-1, ny-1)  # x, y, w, h
        # air: top, right, bottom, left; figure 'squares': by x, by y
        nodes = [top, right, bottom, left, nx-1, ny-1]

        other_data = {'type': 'triangle', 'form': form}
        mesh = Mesh(nodes, other_data)

        return box, mesh, 1  # '1' for Triangle

    def get_pos_triangle(self, x, y, form, nx=2, ny=2, top=0, right=0, bottom=0, left=0):
        box = (x, y, nx-1, ny-1)  # x, y, w, h
        nodes = [top, right, bottom, left, nx-1, ny-1]
        other_data = {'type': 'triangle', 'form': form}
        mesh = Mesh(nodes, other_data)

        return box, mesh, 1  # '1' for Triangle

    def expand_fig(self, ind, side_code, new_data):
        prim = self.fig.shape[ind]
        self.fig.adopt_primitive(*new_data)
        new_prim = self.fig.shape[-1]
        prim.connect(side_code, new_prim)
        new_prim.connect((side_code+2) % 4, prim)  # shave opposite side

    def check_mesh(self, input, elems_test, coords_test, material_test):
        self.fig.adopt_primitive(*input)
        self.check_figure(elems_test, coords_test, material_test)

    def check_figure(self, elems_test, coords_test, material_test):
        """
        elements_test — список элементов, что будут образованы разбиением. Элемент задается индексами трёх формирующих его вершин
        coords_test — список координат узлов. Индекс узла указан третьим числом в строке
        """
        self.fig.save_mesh(OUTPUT_FILENAME)
        res = subprocess.run(["./Sorter.py", OUTPUT_FILENAME, "True", "True"]).returncode

        if res == 0:
            self.check_output(elems_test, coords_test, material_test)
        else:
            raise Exception("Can't run Sorter")

    def check_output(self, elems_test, coords_test, material_test):
        with open(OUTPUT_FILENAME + "_sorted_elements", "r") as f:
            triangles = f.readlines()
            print(triangles)
            self.assertEqual(triangles, elems_test, "Wrong triangles formed for")

        with open(OUTPUT_FILENAME + "_sorted_nodes", "r") as f:
            coords = [[float(elem) for elem in line.split(' ')] for line in f.readlines()]  # convert lines to Python's list[list]
            print(coords)
            self.assertEqual(coords, coords_test, "Wrong coordinates")

        with open(OUTPUT_FILENAME + "_sorted_elements-material", "r") as f:
            elements_material = [int(elem) for elem in f.readlines()]
            print(elements_material)
            self.assertEqual(elements_material, material_test, "Wrong material")

    def check_exporting(self, compare):
        self.fig.exporting(EXPORT_OUTPUT_FILENAME)
        with open(EXPORT_OUTPUT_FILENAME, "r") as exported:
            self.assertEqual(exported.readlines(), compare, "Figure build unexpected")

    def generate_grid(self, nx, ny, offset=0):
        elems = list()
        for j in range(ny-1):
            for i in range(nx-1):
                curr = offset + i + (nx*j)
                next_ = curr + 1
                next_line_curr = curr + nx
                next_line_next = next_line_curr + 1
                elems.append("{} {} {}\n".format(curr, next_line_curr, next_line_next))
                elems.append("{} {} {}\n".format(curr, next_, next_line_next))

        coord = list()
        for j in range(ny):
            for i in range(nx):
                coord.append([i, j])

        return elems, coord
