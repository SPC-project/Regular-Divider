"""
    Test cases for single triangle primitive with/without air

    Naming convention: NxMTypeK_airL
        N – width of the primitive in nodes
        M – height of the primitive in nodes
        K – see 'doc/forms_of_triangles.png' for details
        L – thickness of air layer in nodes
"""

import sys
import unittest

from test.AbstractTest import AbstractTest
from PyQt5.QtWidgets import QApplication
app = QApplication(sys.argv)


class NoAir(AbstractTest):
    """
    Check how meshing work on pure-Figure rectangles

    'self.get_triangle(type, nx, ny)' generates pair (box, mesh), that is used by
        'self.check_mesh' for creating and meshing the figure.
        'type' (see 'doc/forms_of_triangles.png' for details)
    Variables 'e', 'c' and 'm' store expected result for meshing
    """
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
        m = [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0]
        self.check_mesh(tri, e, c, m)

    def test_5x5Type1(self):
        tri = self.get_triangle(1, 5, 5)
        e, c = self.generate_distorted_diagonal_grid(5, 5)
        m = [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1]
        self.check_mesh(tri, e, c, m)


class Air_OneElementFigure(AbstractTest):
    def test_2x2Type0_air1(self):
        air = 1
        tri = self.get_triangle(0, 2, 2, air, air, air, air)
        e, c = self.generate_grid(4, 4)
        m = [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.check_mesh(tri, e, c, m)

    def test_2x2Type0_air2(self):
        air = 2
        tri = self.get_triangle(0, 2, 2, air, air, air, air)
        e, c = self.generate_grid(6, 6)
        m = [0]*24 + [1] + [0]*25  # one figure element and rest are air
        self.check_mesh(tri, e, c, m)

    def test_2x2Type1_air1(self):
        air = 1
        tri = self.get_triangle(1, 2, 2, air, air, air, air)
        e, c = self.generate_grid(4, 4)
        e[8] = '5 9 6\n'  # Type 1 produces distorted grid
        e[9] = '6 9 10\n'
        m = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        self.check_mesh(tri, e, c, m)

    def test_2x2Type1_air2(self):
        air = 2
        tri = self.get_triangle(1, 2, 2, air, air, air, air)
        e, c = self.generate_grid(6, 6)
        e[24] = '14 20 15\n'  # Type 1 produces distorted grid
        e[25] = '15 20 21\n'
        m = [0]*25 + [1] + [0]*24  # one figure element and rest are air
        self.check_mesh(tri, e, c, m)

    def test_2x2Type2_air1(self):
        air = 1
        tri = self.get_triangle(2, 2, 2, air, air, air, air)
        e, c = self.generate_grid(4, 4)
        e[8] = '5 9 6\n'  # Type 2 produces distorted grid
        e[9] = '6 9 10\n'
        m = [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.check_mesh(tri, e, c, m)

    def test_2x2Type2_air2(self):
        air = 2
        tri = self.get_triangle(2, 2, 2, air, air, air, air)
        e, c = self.generate_grid(6, 6)
        e[24] = '14 20 15\n'  # Type 1 produces distorted grid
        e[25] = '15 20 21\n'
        m = [0]*24 + [1] + [0]*25  # one figure element and rest are air
        self.check_mesh(tri, e, c, m)

    def test_2x2Type3_air1(self):
        air = 1
        tri = self.get_triangle(3, 2, 2, air, air, air, air)
        e, c = self.generate_grid(4, 4)
        m = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        self.check_mesh(tri, e, c, m)

    def test_2x2Type3_air2(self):
        air = 2
        tri = self.get_triangle(3, 2, 2, air, air, air, air)
        e, c = self.generate_grid(6, 6)
        m = [0]*25 + [1] + [0]*24  # one figure element and rest are air
        self.check_mesh(tri, e, c, m)


class AirCoat(AbstractTest):
    """ Test case for primitive with a full air surrounding """
    def test_3x3Type0_air1(self):
        tri, e, c = self.generate_test_triangle_case(0, 3, 1)
        m = [0] * 10 + [1] + [0]*7 + [1]*3 + [0]*11
        self.check_mesh(tri, e, c, m)

    def test_3x3Type0_air2(self):
        tri, e, c = self.generate_test_triangle_case(0, 3, 2)
        m = [0] * 28 + [1] + [0]*11 + [1]*3 + [0]*29
        self.check_mesh(tri, e, c, m)

    def test_3x3Type1_air1(self):
        tri, e, c = self.generate_test_triangle_case(1, 3, 1)
        e[12] = "7 12 8\n"
        e[13] = "8 13 12\n"
        e[18] = "11 16 12\n"
        e[19] = "12 17 16\n"
        m = [0] * 10 + [1] + [0]*7 + [1]*3 + [0]*11
        self.check_mesh(tri, e, c, m)

    def test_3x3Type1_air2(self):
        tri, e, c = self.generate_test_triangle_case(1, 3, 2)
        e[30] = "17 24 18\n"
        e[31] = "18 25 24\n"
        e[40] = "23 30 24\n"
        e[41] = "24 31 30\n"
        m = [0] * 31 + [1] + [0]*9 + [1]*3 + [0]*28
        self.check_mesh(tri, e, c, m)

    def test_3x3Type2_air1(self):
        tri, e, c = self.generate_test_triangle_case(2, 3, 1)
        e[12] = "7 12 8\n"
        e[13] = "8 13 12\n"
        e[18] = "11 16 12\n"
        e[19] = "12 17 16\n"
        m = [0] * 10 + [1]*3 + [0]*5 + [1] + [0]*13
        self.check_mesh(tri, e, c, m)

    def test_3x3Type2_air2(self):
        tri, e, c = self.generate_test_triangle_case(2, 3, 2)
        e[30] = "17 24 18\n"
        e[31] = "18 25 24\n"
        e[40] = "23 30 24\n"
        e[41] = "24 31 30\n"
        m = [0] * 28 + [1]*3 + [0]*9 + [1] + [0]*31
        self.check_mesh(tri, e, c, m)

    def test_3x3Type3_air1(self):
        tri, e, c = self.generate_test_triangle_case(3, 3, 1)
        m = [0] * 11 + [1]*3 + [0]*7 + [1] + [0]*10
        self.check_mesh(tri, e, c, m)

    def test_3x3Type3_air2(self):
        tri, e, c = self.generate_test_triangle_case(3, 3, 2)
        m = [0] * 29 + [1]*3 + [0]*11 + [1] + [0]*28
        self.check_mesh(tri, e, c, m)


class OneBareSide(AbstractTest):
    def test_2x2Type0_left(self):
        tri = self.get_triangle(0, 3, 3, 1, 1, 1, 0)
        e, c = self.generate_grid(4, 5)
        m = [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.check_mesh(tri, e, c, m)


if __name__ == '__main__':
    unittest.main()
