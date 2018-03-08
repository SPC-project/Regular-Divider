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
        """nx, ny – amount of nodes by OX and OY axes"""
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

    def generate_testCase_rectangle(self, N, flag_top, flag_right, flag_bottom, flag_left, air=1):
        air_top = air*flag_top
        air_right = air*flag_right
        air_bottom = air*flag_bottom
        air_left = air*flag_left
        rect = self.get_rectangle(N, N, air_top, air_right, air_bottom, air_left)
        e, c = self.generate_grid(air_left + N + air_right, air_top + N + air_bottom)

        N -= 1  # switch to length in elements (2x2 grid produces two elements)
        material = []
        row_len = (air_left + N + air_right)*2
        for j in range(0, air_top):
            material += [0]*row_len
        for j in range(0, N):
            material += [0]*air_left*2 + [1]*N*2 + [0]*air_right*2
        for j in range(0, air_bottom):
            material += [0]*row_len

        # print(material)
        self.check_mesh(rect, e, c, material)

    def generate_testCase_triangle(self, type_, dimensions, air):
        """ Return:
            - tuple for Regular-Divider to create mesh
            - expected elements (each is three indexes of nodes forming it)
            - expected coordinates of nodes
        """
        triangle = self.get_triangle(type_, dimensions, dimensions, air, air, air, air)
        elems, coords = self.generate_grid(dimensions + air*2, dimensions + air*2)

        return triangle, elems, coords

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
            # print(triangles)
            self.assertEqual(triangles, elems_test, "Wrong triangles formed for")

        with open(OUTPUT_FILENAME + "_sorted_nodes", "r") as f:
            coords = [[float(elem) for elem in line.split(' ')] for line in f.readlines()]  # convert lines to Python's list[list]
            # print(coords)
            self.assertEqual(coords, coords_test, "Wrong coordinates")

        with open(OUTPUT_FILENAME + "_sorted_elements-material", "r") as f:
            elements_material = [int(elem) for elem in f.readlines()]
            # print(elements_material)
            self.assertEqual(elements_material, material_test, "Wrong material")

    def check_exporting(self, compare):
        self.fig.exporting(EXPORT_OUTPUT_FILENAME)
        with open(EXPORT_OUTPUT_FILENAME, "r") as exported:
            self.assertEqual(exported.readlines(), compare, "Figure build unexpected")

    def generate_grid(self, nx, ny, offset_index=0, offset_x=0, offset_y=0):
        elems = list()
        for j in range(ny-1):
            for i in range(nx-1):
                curr = offset_index + i + (nx*j)
                next_ = curr + 1
                next_line_curr = curr + nx
                next_line_next = next_line_curr + 1
                elems.append("{} {} {}\n".format(curr, next_line_curr, next_line_next))
                elems.append("{} {} {}\n".format(curr, next_, next_line_next))

        coord = list()
        for j in range(ny):
            for i in range(nx):
                coord.append([i + offset_x, j + offset_y])

        return elems, coord

    def generate_distorted_diagonal_grid(self, nx, ny, offset_index=0, offset_x=0, offset_y=0):
        elems = list()
        for j in range(ny-1):
            for i in range(nx-1):
                curr = offset_index + i + (nx*j)
                next_ = curr + 1
                next_line_curr = curr + nx
                next_line_next = next_line_curr + 1
                if i == (nx-2) - j:
                    elems.append("{} {} {}\n".format(curr, next_line_curr, next_))
                    elems.append("{} {} {}\n".format(next_, next_line_next, next_line_curr))
                else:
                    elems.append("{} {} {}\n".format(curr, next_line_curr, next_line_next))
                    elems.append("{} {} {}\n".format(curr, next_, next_line_next))

        coord = list()
        for j in range(ny):
            for i in range(nx):
                coord.append([i + offset_x, j + offset_y])

        return elems, coord
