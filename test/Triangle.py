import unittest
import sys
import os

from PyQt5.QtWidgets import QApplication
from src.figure import Figure, Output
from src.primitive import Mesh
app = QApplication(sys.argv)


class FakeParentApp:
    def setText(self, txt):
        pass

    def adjustSize(self):
        pass

    def emit(self):
        pass


class TestSoloTriangleMesh(unittest.TestCase):
    """
    Тестируем работа figure/save_mesh
    """
    def setUp(self):
        holder = FakeParentApp()
        self.fig = Figure(holder, holder, holder, holder)
        self.fig.world_size = 10
        self.fig.start_x = 0
        self.fig.start_y = 0

    def get_triangle(self, form, nx=2, ny=2, horizontal=0, vertical=0, w=1, h=1):
        box = (0.0, 0.0, w, h)  # x, y, w, h
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

    def test_noAirTwoElementsExportImport(self):
        self.fig.adopt_primitive(*self.get_triangle(0))

        filename = "./test/triangle_rectangle.d40do"
        self.fig.exporting(filename)
        self.fig.importing(filename)
        self.assertEqual(len(self.fig.shape), 1, "Should be exactly one primitive")

        type_ = self.fig.shape[0].mesh.data["type"]
        self.assertEqual(type_, "triangle", "Type should be triangle")
        os.remove(filename)

    def check_mesh(self, input, elems_test, coords_test, name):
        """
        elements_test — список элементов, что будут образованы разбиением. Элемент задается индексами трёх формирующих его вершин
        coords_test — список координат узлов. Индекс узла указан третьим числом в строке
        """
        self.fig.adopt_primitive(*input)
        filename = "./test/check_triangle.pmd"
        self.fig.save_mesh(filename)

        with open(Output.TEMP_DIR + Output.FILENAMES[0] + ".tmp", "r") as f:
            triangles = f.readlines()
            self.assertEqual(triangles, elems_test, "Wrong triangles formed for: " + name)

        with open(Output.TEMP_DIR + Output.FILENAMES[1] + ".tmp", "r") as f:
            coords = [[float(elem) for elem in line.split(' ')] for line in f.readlines()]  # convert lines to Python's list[list]
            counter = 0
            for line in coords:
                self.assertEqual(line[2], counter, "Numeration break for: " + name)
                del line[2]
                counter += 1
            print(coords)
            self.assertEqual(coords, coords_test, "Wrong coordinates for: " + name)

        # os.remove(filename)

    def test_3x3TriangleType0_noAir(self):
        tri = self.get_triangle(0, 3, 3, 0, 0, 2, 2)
        elements_test = ['1 3 4\n', '1 2 4\n', '0 1 2\n', '2 4 5\n']
        coords_test = [[0, 0], [0, 1], [1, 1], [0, 2], [1, 2], [2, 2]]
        self.check_mesh(tri, elements_test, coords_test, "3x3 type 0")

    def test_3x3TriangleType1_noAir(self):
        tri = self.get_triangle(1, 3, 3, 0, 0, 2, 2)
        elements_test = ['1 3 4\n', '1 2 4\n', '0 2 1\n', '1 3 5\n']
        coords_test = [[2, 0], [1, 1], [2, 1], [1, 2], [2, 2], [0, 2]]
        self.check_mesh(tri, elements_test, coords_test, "3x3 type 1")

    def test_3x3TriangleType2_noAir(self):
        tri = self.get_triangle(2, 3, 3, 0, 0, 2, 2)
        elements_test = ['0 2 3\n', '0 1 3\n', '2 4 3\n', '1 3 5\n']
        coords_test = [[0, 0], [1, 0], [0, 1], [1, 1], [0, 2], [2, 0]]
        self.check_mesh(tri, elements_test, coords_test, "3x3 type 2")

    def test_3x3TriangleType3_noAir(self):
        tri = self.get_triangle(3, 3, 3, 0, 0, 2, 2)
        elements_test = ['0 2 3\n', '0 1 3\n', '4 0 2\n', '2 3 5\n']
        coords_test = [[1, 0], [2, 0], [1, 1], [2, 1], [0, 0], [2, 2]]
        self.check_mesh(tri, elements_test, coords_test, "3x3 type 3")

    def test_3x3TriangleType0_withSingleAirLayer(self):
        tri = self.get_triangle(0, 3, 3, 1, 1, 2, 2)
        elements_test = ['0 2 3\n', '0 1 3\n', '2 4 5\n', '2 3 5\n', '4 6 7\n', '4 5 7\n', '8 11 12\n', '8 9 12\n', '9 12 13\n', '9 10 13\n', '15 17 18\n', '15 16 18\n', '14 15 16\n', '16 18 19\n']
        coords_test = [[-1, 0], [0, 0], [-1, 1], [0, 1], [-1, 2], [0, 2], [-1, 3], [0, 3], [0, 2], [1, 2], [2, 2], [0, 3], [1, 3], [2, 3], [0, 0], [0, 1], [1, 1], [0, 2], [1, 2], [2, 2]]
        self.check_mesh(tri, elements_test, coords_test, "3x3 type 0 with air")

    def test_4x4TriangleType0_noAir(self):
        tri = self.get_triangle(0, 4, 4, 0, 0, 3, 3)

        elements_test = ['1 3 4\n', '1 2 4\n', '3 5 6\n', '3 4 6\n',
                         '7 9 10\n', '7 8 10\n',
                         '0 1 2\n', '2 4 8\n', '8 10 11\n']
        first_node = [[0, 0]]
        first_rectangle = [[0.0, 1.0], [1.0, 1.0], [0.0, 2.0], [1.0, 2.0], [0.0, 3.0], [1.0, 3.0]]
        second_rectangle = [[1.0, 2.0], [2.0, 2.0], [1.0, 3.0], [2.0, 3.0]]
        last_node = [[3, 3]]
        coords_test = first_node + first_rectangle + second_rectangle + last_node

        self.check_mesh(tri, elements_test, coords_test, "4x4 type 0")

    def test_4x4TriangleType1_noAir(self):
        tri = self.get_triangle(1, 4, 4, 0, 0, 3, 3)

        elements_test = ['1 3 4\n', '1 2 4\n', '3 5 6\n', '3 4 6\n',
                         '7 9 10\n', '7 8 10\n',
                         '0 2 1\n', '1 3 7\n', '7 9 11\n']

        first_node = [[3, 0]]
        first_rectangle = [[2.0, 1.0], [3.0, 1.0], [2.0, 2.0], [3.0, 2.0], [2.0, 3.0], [3.0, 3.0]]
        second_rectangle = [[1.0, 2.0], [2.0, 2.0], [1.0, 3.0], [2.0, 3.0]]
        last_node = [[0, 3]]
        coords_test = first_node + first_rectangle + second_rectangle + last_node

        self.check_mesh(tri, elements_test, coords_test, "4x4 type 1")

    def test_4x4TriangleType2_noAir(self):
        tri = self.get_triangle(2, 4, 4, 0, 0, 3, 3)

        elements_test = ['0 2 3\n', '0 1 3\n', '2 4 5\n', '2 3 5\n',
                         '6 8 9\n', '6 7 9\n',
                         '4 10 5\n', '8 5 9\n', '7 9 11\n']

        first_rectangle = [[0, 0], [1, 0], [0, 1], [1, 1], [0, 2], [1, 2]]
        second_rectangle = [[1, 0], [2, 0], [1, 1], [2, 1]]
        edge_nodes = [[0, 3], [3, 0]]
        coordinates_test = first_rectangle + second_rectangle + edge_nodes

        self.check_mesh(tri, elements_test, coordinates_test, "4x4 type 2")

    def test_4x4TriangleType3_noAir(self):
        tri = self.get_triangle(3, 4, 4, 0, 0, 3, 3)

        elements_test = ['0 2 3\n', '0 1 3\n', '2 4 5\n', '2 3 5\n',
                         '6 8 9\n', '6 7 9\n',
                         '10 6 8\n', '8 9 4\n', '4 5 11\n']

        first_rectangle = [[2.0, 0.0], [3.0, 0.0], [2.0, 1.0], [3.0, 1.0], [2.0, 2.0], [3.0, 2.0]]
        second_rectangle = [[1.0, 0.0], [2.0, 0.0], [1.0, 1.0], [2.0, 1.0]]
        edge_nodes = [[0, 0], [3, 3]]
        coordinates_test = first_rectangle + second_rectangle + edge_nodes

        self.check_mesh(tri, elements_test, coordinates_test, "4x4 type 3")

    def test_4x4TriangleType0_withSingleAirLayer(self):
        tri = self.get_triangle(0, 4, 4, 1, 1, 3, 3)

        air_left = ['0 2 3\n', '0 1 3\n', '2 4 5\n', '2 3 5\n', '4 6 7\n', '4 5 7\n', '6 8 9\n', '6 7 9\n']
        air_bottom = ['10 14 15\n', '10 11 15\n', '11 15 16\n', '11 12 16\n', '12 16 17\n', '12 13 17\n']
        figure_first = ['18 20 21\n', '18 19 21\n', '20 22 23\n', '20 21 23\n']
        figure_second = ['24 26 27\n', '24 25 27\n']
        elements_example = air_left + air_bottom + figure_first + figure_second

        coords_al = [[-1.0, 0.0], [0.0, 0.0], [-1.0, 1.0], [0.0, 1.0], [-1.0, 2.0], [0.0, 2.0], [-1.0, 3.0], [0.0, 3.0], [-1.0, 4.0], [0.0, 4.0]]
        coords_ab = [[0.0, 3.0], [1.0, 3.0], [2.0, 3.0], [3.0, 3.0], [0.0, 4.0], [1.0, 4.0], [2.0, 4.0], [3.0, 4.0]]
        coords_ff = [[0.0, 1.0], [1.0, 1.0], [0.0, 2.0], [1.0, 2.0], [0.0, 3.0], [1.0, 3.0]]
        coords_fs = [[1.0, 2.0], [2.0, 2.0], [1.0, 3.0], [2.0, 3.0]]
        coords_example = coords_al + coords_ab + coords_ff + coords_fs

        self.check_mesh(tri, elements_example, coords_example, "4x4 type 0 with air")

    def test_4x4TriangleType1_withSingleAirLayer(self):
        tri = self.get_triangle(1, 4, 4, 1, 1, 3, 3)

        air_left = ['0 2 3\n', '0 1 3\n', '2 4 5\n', '2 3 5\n', '4 6 7\n', '4 5 7\n', '6 8 9\n', '6 7 9\n']
        air_bottom = ['10 14 15\n', '10 11 15\n', '11 15 16\n', '11 12 16\n', '12 16 17\n', '12 13 17\n']
        figure_first = ['18 20 21\n', '18 19 21\n', '20 22 23\n', '20 21 23\n']
        figure_second = ['24 26 27\n', '24 25 27\n']
        elements_example = air_left + air_bottom + figure_first + figure_second

        coords_example = [[3.0, 0.0], [4.0, 0.0], [3.0, 1.0], [4.0, 1.0], [3.0, 2.0], [4.0, 2.0], [3.0, 3.0], [4.0, 3.0], [3.0, 4.0], [4.0, 4.0], [0.0, 3.0], [1.0, 3.0], [2.0, 3.0], [3.0, 3.0], [0.0, 4.0], [1.0, 4.0], [2.0, 4.0], [3.0, 4.0], [2.0, 1.0], [3.0, 1.0], [2.0, 2.0], [3.0, 2.0], [2.0, 3.0], [3.0, 3.0], [1.0, 2.0], [2.0, 2.0], [1.0, 3.0], [2.0, 3.0]]

        self.check_mesh(tri, elements_example, coords_example, "4x4 type 1 with air")

    def test_4x4TriangleType2_withSingleAirLayer(self):
        tri = self.get_triangle(2, 4, 4, 1, 1, 3, 3)

        air_left = ['0 2 3\n', '0 1 3\n', '2 4 5\n', '2 3 5\n', '4 6 7\n', '4 5 7\n', '6 8 9\n', '6 7 9\n']
        air_bottom = ['10 14 15\n', '10 11 15\n', '11 15 16\n', '11 12 16\n', '12 16 17\n', '12 13 17\n']
        figure_first = ['18 20 21\n', '18 19 21\n', '20 22 23\n', '20 21 23\n']
        figure_second = ['24 26 27\n', '24 25 27\n']
        elements_example = air_left + air_bottom + figure_first + figure_second

        coords_example = [[-1.0, -1.0], [0.0, -1.0], [-1.0, 0.0], [0.0, 0.0], [-1.0, 1.0], [0.0, 1.0], [-1.0, 2.0], [0.0, 2.0], [-1.0, 3.0], [0.0, 3.0], [0.0, -1.0], [1.0, -1.0], [2.0, -1.0], [3.0, -1.0], [0.0, 0.0], [1.0, 0.0], [2.0, 0.0], [3.0, 0.0], [0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [0.0, 2.0], [1.0, 2.0], [1.0, 0.0], [2.0, 0.0], [1.0, 1.0], [2.0, 1.0]]

        self.check_mesh(tri, elements_example, coords_example, "4x4 type 2 with air")

    def test_4x4TriangleType3_withSingleAirLayer(self):
        tri = self.get_triangle(3, 4, 4, 1, 1, 3, 3)

        air_left = ['0 2 3\n', '0 1 3\n', '2 4 5\n', '2 3 5\n', '4 6 7\n', '4 5 7\n', '6 8 9\n', '6 7 9\n']
        air_bottom = ['10 14 15\n', '10 11 15\n', '11 15 16\n', '11 12 16\n', '12 16 17\n', '12 13 17\n']
        figure_first = ['18 20 21\n', '18 19 21\n', '20 22 23\n', '20 21 23\n']
        figure_second = ['24 26 27\n', '24 25 27\n']
        elements_example = air_left + air_bottom + figure_first + figure_second

        coords_example = [[3.0, -1.0], [4.0, -1.0], [3.0, 0.0], [4.0, 0.0], [3.0, 1.0], [4.0, 1.0], [3.0, 2.0], [4.0, 2.0], [3.0, 3.0], [4.0, 3.0], [0.0, -1.0], [1.0, -1.0], [2.0, -1.0], [3.0, -1.0], [0.0, 0.0], [1.0, 0.0], [2.0, 0.0], [3.0, 0.0], [2.0, 0.0], [3.0, 0.0], [2.0, 1.0], [3.0, 1.0], [2.0, 2.0], [3.0, 2.0], [1.0, 0.0], [2.0, 0.0], [1.0, 1.0], [2.0, 1.0]]

        self.check_mesh(tri, elements_example, coords_example, "4x4 type 3 with air")


if __name__ == '__main__':
    unittest.main()
