import sys
import unittest

from test.AbstractTest import AbstractTest
from PyQt5.QtWidgets import QApplication
app = QApplication(sys.argv)


class NoAir(AbstractTest):
    def test_2x2Type0(self):
        tri = self.get_triangle(0, 2, 2)
        e, c = self.generate_grid(2, 2)
        m = [1, 0]
        self.check_mesh(tri, e, c, m)

    def test_2x2Type1(self):
        tri = self.get_triangle(1, 2, 2)
        elements_test = ['0 2 1\n', '1 2 3\n']
        coords_test = [[0, 0], [1, 0], [0, 1], [1, 1]]
        material_test = [0, 1]
        self.check_mesh(tri, elements_test, coords_test, material_test)

    def test_2x2Type2(self):
        tri = self.get_triangle(2, 2, 2)
        elements_test = ['0 2 1\n', '1 2 3\n']
        coords_test = [[0, 0], [1, 0], [0, 1], [1, 1]]
        material_test = [1, 0]
        self.check_mesh(tri, elements_test, coords_test, material_test)

    def test_2x2Type3(self):
        tri = self.get_triangle(3, 2, 2)
        e, c = self.generate_grid(2, 2)
        m = [0, 1]
        self.check_mesh(tri, e, c, m)

    def test_3x3Type0(self):
        tri = self.get_triangle(0, 3, 3)
        elements_test, coords_test = self.generate_grid(3, 3)
        material_test = [1, 0, 0, 0, 1, 1, 1, 0]
        self.check_mesh(tri, elements_test, coords_test, material_test)

    def test_3x3Type1(self):
        tri = self.get_triangle(1, 3, 3)
        elements_test = ['0 3 4\n', '0 1 4\n', '1 4 2\n', '2 5 4\n', '3 6 4\n', '4 7 6\n', '4 7 8\n', '4 5 8\n']
        coords_test = [[0, 0], [1, 0], [2, 0],
                       [0, 1], [1, 1], [2, 1],
                       [0, 2], [1, 2], [2, 2]]
        material_test = [0, 0, 0, 1, 0, 1, 1, 1]
        self.check_mesh(tri, elements_test, coords_test, material_test)

    def test_3x3Type2(self):
        tri = self.get_triangle(2, 3, 3)
        elements_test = ['0 3 4\n', '0 1 4\n', '1 4 2\n', '2 5 4\n', '3 6 4\n', '4 7 6\n', '4 7 8\n', '4 5 8\n']
        coords_test = [[0, 0], [1, 0], [2, 0],
                       [0, 1], [1, 1], [2, 1],
                       [0, 2], [1, 2], [2, 2]]
        material_test = [1, 1, 1, 0, 1, 0, 0, 0]
        self.check_mesh(tri, elements_test, coords_test, material_test)

    def test_3x3Type3(self):
        tri = self.get_triangle(3, 3, 3)
        elements_test, coords_test = self.generate_grid(3, 3)
        material_test = [0, 1, 1, 1, 0, 0, 0, 1]
        self.check_mesh(tri, elements_test, coords_test, material_test)

    def test_4x4Type0(self):
        tri = self.get_triangle(0, 4, 4)
        e, c = self.generate_grid(4, 4)
        m = [1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0]
        self.check_mesh(tri, e, c, m)

    def test_4x4Type1(self):
        tri = self.get_triangle(1, 4, 4,)

        elems = ['0 4 5\n', '0 1 5\n', '1 5 6\n', '1 2 6\n', '2 6 3\n', '3 7 6\n', '4 8 9\n', '4 5 9\n', '5 9 6\n', '6 10 9\n', '6 10 11\n', '6 7 11\n', '8 12 9\n', '9 13 12\n', '9 13 14\n', '9 10 14\n', '10 14 15\n', '10 11 15\n']
        coords_test = [[0, 0], [1, 0], [2, 0], [3, 0],
                       [0, 1], [1, 1], [2, 1], [3, 1],
                       [0, 2], [1, 2], [2, 2], [3, 2],
                       [0, 3], [1, 3], [2, 3], [3, 3]]
        material_test = [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1]
        self.check_mesh(tri, elems, coords_test, material_test)

    def test_4x4Type2(self):
        tri = self.get_triangle(2, 4, 4,)

        elems = ['0 4 5\n', '0 1 5\n', '1 5 6\n', '1 2 6\n', '2 6 3\n', '3 7 6\n', '4 8 9\n', '4 5 9\n', '5 9 6\n', '6 10 9\n', '6 10 11\n', '6 7 11\n', '8 12 9\n', '9 13 12\n', '9 13 14\n', '9 10 14\n', '10 14 15\n', '10 11 15\n']
        coords_test = [[0, 0], [1, 0], [2, 0], [3, 0],
                       [0, 1], [1, 1], [2, 1], [3, 1],
                       [0, 2], [1, 2], [2, 2], [3, 2],
                       [0, 3], [1, 3], [2, 3], [3, 3]]
        material_test = [1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0]
        self.check_mesh(tri, elems, coords_test, material_test)

    def test_4x4Type3(self):
        tri = self.get_triangle(3, 4, 4)
        e, c = self.generate_grid(4, 4)
        m = [0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1]
        self.check_mesh(tri, e, c, m)

    def test_5x5Type0(self):
        tri = self.get_triangle(0, 5, 5)
        e, c = self.generate_grid(5, 5)
        m = [0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1]
        self.check_mesh(tri, e, c, m)

    def test_5x5Type1(self):
        tri = self.get_triangle(1, 5, 5)
        e, c = self.generate_distorted_diagonal_grid(5, 5)
        m = [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1]
        self.check_mesh(tri, e, c, m)


class SingleAirLayer(AbstractTest):
    def test_2x2Type0(self):
        tri = self.get_triangle(0, 2, 2, 1, 1, 1, 1)
        e, c = self.generate_grid(4, 4)
        m = [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.check_mesh(tri, e, c, m)

    def test_2x2Type1(self):
        tri = self.get_triangle(1, 2, 2, 1, 1, 1, 1)
        e = ['0 4 5\n', '0 1 5\n', '1 5 6\n', '1 2 6\n', '2 6 7\n', '2 3 7\n', '4 8 9\n', '4 5 9\n', '5 9 6\n', '6 9 10\n', '6 10 11\n', '6 7 11\n', '8 12 13\n', '8 9 13\n', '9 13 14\n', '9 10 14\n', '10 14 15\n', '10 11 15\n']
        c = [[0, 0], [1, 0], [2, 0], [3, 0],
             [0, 1], [1, 1], [2, 1], [3, 1],
             [0, 2], [1, 2], [2, 2], [3, 2],
             [0, 3], [1, 3], [2, 3], [3, 3]]
        m = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        self.check_mesh(tri, e, c, m)

    def test_2x2Type2(self):
        tri = self.get_triangle(2, 2, 2, 1, 1, 1, 1)
        e = ['0 4 5\n', '0 1 5\n', '1 5 6\n', '1 2 6\n', '2 6 7\n', '2 3 7\n', '4 8 9\n', '4 5 9\n', '5 9 6\n', '6 9 10\n', '6 10 11\n', '6 7 11\n', '8 12 13\n', '8 9 13\n', '9 13 14\n', '9 10 14\n', '10 14 15\n', '10 11 15\n']
        c = [[0, 0], [1, 0], [2, 0], [3, 0],
             [0, 1], [1, 1], [2, 1], [3, 1],
             [0, 2], [1, 2], [2, 2], [3, 2],
             [0, 3], [1, 3], [2, 3], [3, 3]]
        m = [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.check_mesh(tri, e, c, m)

    def test_2x2Type3(self):
        tri = self.get_triangle(3, 2, 2, 1, 1, 1, 1)
        e, c = self.generate_grid(4, 4)
        m = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        self.check_mesh(tri, e, c, m)


if __name__ == '__main__':
    unittest.main()
