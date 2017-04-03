import sys
import os
import unittest

from test.abstractTest import AbstractTest
from PyQt5.QtWidgets import QApplication
app = QApplication(sys.argv)


class Test_Triangle(AbstractTest):
    """
    Тестируем работа figure/save_mesh
    """
    def test_noAirTwoElementsExportImport(self):
        self.fig.adopt_primitive(*self.get_triangle(0))

        filename = "./test/triangle.d40do"
        self.fig.exporting(filename)
        self.fig.importing(filename)
        self.assertEqual(len(self.fig.shape), 1, "Should be exactly one primitive")

        type_ = self.fig.shape[0].mesh.data["type"]
        self.assertEqual(type_, "triangle", "Type should be triangle")
        os.remove(filename)

    def test_3x3TriangleType0_noAir(self):
        tri = self.get_triangle(0, 3, 3, 0, 0)
        elements_test = ['1 3 4\n', '1 2 4\n', '0 1 2\n', '2 4 5\n']
        coords_test = [[0, 0], [0, 1], [1, 1], [0, 2], [1, 2], [2, 2]]
        self.check_mesh(tri, elements_test, coords_test)

    def test_3x3TriangleType1_noAir(self):
        tri = self.get_triangle(1, 3, 3, 0, 0)
        elements_test = ['1 3 4\n', '1 2 4\n', '0 2 1\n', '1 3 5\n']
        coords_test = [[2, 0], [1, 1], [2, 1], [1, 2], [2, 2], [0, 2]]
        self.check_mesh(tri, elements_test, coords_test)

    def test_3x3TriangleType2_noAir(self):
        tri = self.get_triangle(2, 3, 3, 0, 0)
        elements_test = ['0 2 3\n', '0 1 3\n', '2 4 3\n', '1 3 5\n']
        coords_test = [[0, 0], [1, 0], [0, 1], [1, 1], [0, 2], [2, 0]]
        self.check_mesh(tri, elements_test, coords_test)

    def test_3x3TriangleType3_noAir(self):
        tri = self.get_triangle(3, 3, 3, 0, 0)
        elements_test = ['0 2 3\n', '0 1 3\n', '4 0 2\n', '2 3 5\n']
        coords_test = [[1, 0], [2, 0], [1, 1], [2, 1], [0, 0], [2, 2]]
        self.check_mesh(tri, elements_test, coords_test)

    def test_3x3TriangleType0_withSingleAirLayer(self):
        tri = self.get_triangle(0, 3, 3, 1, 1)
        elements_test = ['0 2 3\n', '0 1 3\n', '2 4 5\n', '2 3 5\n', '4 6 7\n', '4 5 7\n', '8 11 12\n', '8 9 12\n', '9 12 13\n', '9 10 13\n', '15 17 18\n', '15 16 18\n', '14 15 16\n', '16 18 19\n']
        coords_test = [[-1, 0], [0, 0], [-1, 1], [0, 1], [-1, 2], [0, 2], [-1, 3], [0, 3], [0, 2], [1, 2], [2, 2], [0, 3], [1, 3], [2, 3], [0, 0], [0, 1], [1, 1], [0, 2], [1, 2], [2, 2]]
        self.check_mesh(tri, elements_test, coords_test, "3x3 type 0 with air")

    def test_4x4TriangleType0_noAir(self):
        tri = self.get_triangle(0, 4, 4, 0, 0)

        elements_test = ['1 3 4\n', '1 2 4\n', '3 5 6\n', '3 4 6\n',
                         '7 9 10\n', '7 8 10\n',
                         '0 1 2\n', '2 4 8\n', '8 10 11\n']
        first_node = [[0, 0]]
        first_rectangle = [[0.0, 1.0], [1.0, 1.0], [0.0, 2.0], [1.0, 2.0], [0.0, 3.0], [1.0, 3.0]]
        second_rectangle = [[1.0, 2.0], [2.0, 2.0], [1.0, 3.0], [2.0, 3.0]]
        last_node = [[3, 3]]
        coords_test = first_node + first_rectangle + second_rectangle + last_node

        self.check_mesh(tri, elements_test, coords_test)

    def test_4x4TriangleType1_noAir(self):
        tri = self.get_triangle(1, 4, 4, 0, 0)

        elements_test = ['1 3 4\n', '1 2 4\n', '3 5 6\n', '3 4 6\n',
                         '7 9 10\n', '7 8 10\n',
                         '0 2 1\n', '1 3 7\n', '7 9 11\n']

        first_node = [[3, 0]]
        first_rectangle = [[2.0, 1.0], [3.0, 1.0], [2.0, 2.0], [3.0, 2.0], [2.0, 3.0], [3.0, 3.0]]
        second_rectangle = [[1.0, 2.0], [2.0, 2.0], [1.0, 3.0], [2.0, 3.0]]
        last_node = [[0, 3]]
        coords_test = first_node + first_rectangle + second_rectangle + last_node

        self.check_mesh(tri, elements_test, coords_test)

    def test_4x4TriangleType2_noAir(self):
        tri = self.get_triangle(2, 4, 4, 0, 0)

        elements_test = ['0 2 3\n', '0 1 3\n', '2 4 5\n', '2 3 5\n',
                         '6 8 9\n', '6 7 9\n',
                         '4 10 5\n', '8 5 9\n', '7 9 11\n']

        first_rectangle = [[0, 0], [1, 0], [0, 1], [1, 1], [0, 2], [1, 2]]
        second_rectangle = [[1, 0], [2, 0], [1, 1], [2, 1]]
        edge_nodes = [[0, 3], [3, 0]]
        coordinates_test = first_rectangle + second_rectangle + edge_nodes

        self.check_mesh(tri, elements_test, coordinates_test)

    def test_4x4TriangleType3_noAir(self):
        tri = self.get_triangle(3, 4, 4, 0, 0)

        elements_test = ['0 2 3\n', '0 1 3\n', '2 4 5\n', '2 3 5\n',
                         '6 8 9\n', '6 7 9\n',
                         '10 6 8\n', '8 9 4\n', '4 5 11\n']

        first_rectangle = [[2.0, 0.0], [3.0, 0.0], [2.0, 1.0], [3.0, 1.0], [2.0, 2.0], [3.0, 2.0]]
        second_rectangle = [[1.0, 0.0], [2.0, 0.0], [1.0, 1.0], [2.0, 1.0]]
        edge_nodes = [[0, 0], [3, 3]]
        coordinates_test = first_rectangle + second_rectangle + edge_nodes

        self.check_mesh(tri, elements_test, coordinates_test)

    def test_4x4TriangleType0_withSingleAirLayer(self):
        tri = self.get_triangle(0, 4, 4, 1, 1)

        air_left = ['0 2 3\n', '0 1 3\n', '2 4 5\n', '2 3 5\n', '4 6 7\n', '4 5 7\n', '6 8 9\n', '6 7 9\n']
        air_bottom = ['10 14 15\n', '10 11 15\n', '11 15 16\n', '11 12 16\n', '12 16 17\n', '12 13 17\n']
        figure_first = ['19 21 22\n', '19 20 22\n', '21 23 24\n', '21 22 24\n']
        figure_second = ['25 27 28\n', '25 26 28\n']
        hipo = ['18 19 20\n', '20 22 26\n', '26 28 29\n']
        elements_example = air_left + air_bottom + figure_first + figure_second + hipo

        coords_al = [[-1.0, 0.0], [0.0, 0.0], [-1.0, 1.0], [0.0, 1.0], [-1.0, 2.0], [0.0, 2.0], [-1.0, 3.0], [0.0, 3.0], [-1.0, 4.0], [0.0, 4.0]]
        coords_ab = [[0.0, 3.0], [1.0, 3.0], [2.0, 3.0], [3.0, 3.0], [0.0, 4.0], [1.0, 4.0], [2.0, 4.0], [3.0, 4.0]]
        coords_ff = [[0.0, 1.0], [1.0, 1.0], [0.0, 2.0], [1.0, 2.0], [0.0, 3.0], [1.0, 3.0]]
        coords_fs = [[1.0, 2.0], [2.0, 2.0], [1.0, 3.0], [2.0, 3.0]]
        coords_example = coords_al + coords_ab + [[0.0, 0.0]] + coords_ff + coords_fs + [[3.0, 3.0]]

        self.check_mesh(tri, elements_example, coords_example)

    def test_4x4TriangleType1_withSingleAirLayer(self):
        tri = self.get_triangle(1, 4, 4, 1, 1)

        air_left = ['0 2 3\n', '0 1 3\n', '2 4 5\n', '2 3 5\n', '4 6 7\n', '4 5 7\n', '6 8 9\n', '6 7 9\n']
        air_bottom = ['10 14 15\n', '10 11 15\n', '11 15 16\n', '11 12 16\n', '12 16 17\n', '12 13 17\n']
        figure_first = ['19 21 22\n', '19 20 22\n', '21 23 24\n', '21 22 24\n']
        figure_second = ['25 27 28\n', '25 26 28\n']
        hipo = ['18 20 19\n', '19 21 25\n', '25 27 29\n']
        elements_example = air_left + air_bottom + figure_first + figure_second + hipo

        coords_example = [[3.0, 0.0], [4.0, 0.0], [3.0, 1.0], [4.0, 1.0], [3.0, 2.0], [4.0, 2.0], [3.0, 3.0], [4.0, 3.0], [3.0, 4.0], [4.0, 4.0], [0.0, 3.0], [1.0, 3.0], [2.0, 3.0], [3.0, 3.0], [0.0, 4.0], [1.0, 4.0], [2.0, 4.0], [3.0, 4.0], [3.0, 0.0], [2.0, 1.0], [3.0, 1.0], [2.0, 2.0], [3.0, 2.0], [2.0, 3.0], [3.0, 3.0], [1.0, 2.0], [2.0, 2.0], [1.0, 3.0], [2.0, 3.0], [0.0, 3.0]]

        self.check_mesh(tri, elements_example, coords_example)

    def test_4x4TriangleType2_withSingleAirLayer(self):
        tri = self.get_triangle(2, 4, 4, 1, 1)

        air_left = ['0 2 3\n', '0 1 3\n', '2 4 5\n', '2 3 5\n', '4 6 7\n', '4 5 7\n', '6 8 9\n', '6 7 9\n']
        air_bottom = ['10 14 15\n', '10 11 15\n', '11 15 16\n', '11 12 16\n', '12 16 17\n', '12 13 17\n']
        figure_first = ['18 20 21\n', '18 19 21\n', '20 22 23\n', '20 21 23\n']
        figure_second = ['24 26 27\n', '24 25 27\n']
        hipo = ['22 28 23\n', '26 23 27\n', '25 27 29\n']
        elements_example = air_left + air_bottom + figure_first + figure_second + hipo

        coords_example = [[-1.0, -1.0], [0.0, -1.0], [-1.0, 0.0], [0.0, 0.0], [-1.0, 1.0], [0.0, 1.0], [-1.0, 2.0], [0.0, 2.0], [-1.0, 3.0], [0.0, 3.0], [0.0, -1.0], [1.0, -1.0], [2.0, -1.0], [3.0, -1.0], [0.0, 0.0], [1.0, 0.0], [2.0, 0.0], [3.0, 0.0], [0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [0.0, 2.0], [1.0, 2.0], [1.0, 0.0], [2.0, 0.0], [1.0, 1.0], [2.0, 1.0], [0.0, 3.0], [3.0, 0.0]]

        self.check_mesh(tri, elements_example, coords_example)

    def test_4x4TriangleType3_withSingleAirLayer(self):
        tri = self.get_triangle(3, 4, 4, 1, 1)

        air_left = ['0 2 3\n', '0 1 3\n', '2 4 5\n', '2 3 5\n', '4 6 7\n', '4 5 7\n', '6 8 9\n', '6 7 9\n']
        air_bottom = ['10 14 15\n', '10 11 15\n', '11 15 16\n', '11 12 16\n', '12 16 17\n', '12 13 17\n']
        figure_first = ['18 20 21\n', '18 19 21\n', '20 22 23\n', '20 21 23\n']
        figure_second = ['24 26 27\n', '24 25 27\n']
        hipo = ['28 24 26\n', '26 27 22\n', '22 23 29\n']
        elements_example = air_left + air_bottom + figure_first + figure_second + hipo

        coords_example = [[3.0, -1.0], [4.0, -1.0], [3.0, 0.0], [4.0, 0.0], [3.0, 1.0], [4.0, 1.0], [3.0, 2.0], [4.0, 2.0], [3.0, 3.0], [4.0, 3.0], [0.0, -1.0], [1.0, -1.0], [2.0, -1.0], [3.0, -1.0], [0.0, 0.0], [1.0, 0.0], [2.0, 0.0], [3.0, 0.0], [2.0, 0.0], [3.0, 0.0], [2.0, 1.0], [3.0, 1.0], [2.0, 2.0], [3.0, 2.0], [1.0, 0.0], [2.0, 0.0], [1.0, 1.0], [2.0, 1.0], [0.0, 0.0], [3.0, 3.0]]

        self.check_mesh(tri, elements_example, coords_example)


if __name__ == '__main__':
    unittest.main()
