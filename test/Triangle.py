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
        elements_test = ['0 1 2\n', '1 2 3\n']
        coords_test = [[0, 0], [1, 0], [0, 1], [1, 1]]
        material_test = [0, 1]
        self.check_mesh(tri, elements_test, coords_test, material_test)

    def test_2x2Type2(self):
        tri = self.get_triangle(2, 2, 2)
        elements_test = ['0 1 2\n', '1 2 3\n']
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
        tri, elems, coords = self.generate_test_triangle_case(1, 3, 0)
        elems[2] = "1 2 4\n"
        elems[3] = "2 4 5\n"
        elems[4] = "3 4 6\n"
        elems[5] = "4 6 7\n"
        material = [0, 0, 0, 1, 0, 1, 1, 1]
        self.check_mesh(tri, elems, coords, material)

    def test_3x3Type2(self):
        tri, elems, coords = self.generate_test_triangle_case(2, 3, 0)
        elems[2] = "1 2 4\n"
        elems[3] = "2 4 5\n"
        elems[4] = "3 4 6\n"
        elems[5] = "4 6 7\n"
        material = [1]*3 + [0] + [1] + [0]*3
        self.check_mesh(tri, elems, coords, material)

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
        tri, elems, coords = self.generate_test_triangle_case(1, 4, 0)
        elems[4] = "2 3 6\n"
        elems[5] = "3 6 7\n"
        elems[8] = "5 6 9\n"
        elems[9] = "6 9 10\n"
        elems[12] = "8 9 12\n"
        elems[13] = "9 12 13\n"
        material = [0]*5 + [1] + [0]*3 + [1]*3 + [0] + [1]*5
        self.check_mesh(tri, elems, coords, material)

    def test_4x4Type2(self):
        tri, elems, coords = self.generate_test_triangle_case(2, 4, 0)
        elems[4] = "2 3 6\n"
        elems[5] = "3 6 7\n"
        elems[8] = "5 6 9\n"
        elems[9] = "6 9 10\n"
        elems[12] = "8 9 12\n"
        elems[13] = "9 12 13\n"
        material = [1]*5 + [0] + [1]*3 + [0]*3 + [1] + [0]*5
        self.check_mesh(tri, elems, coords, material)

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
        tri, elems, coords = self.generate_test_triangle_case(1, 5, 0)
        elems[6] = "3 4 8\n"
        elems[7] = "4 8 9\n"
        elems[12] = "7 8 12\n"
        elems[13] = "8 12 13\n"
        elems[12] = "7 8 12\n"
        elems[18] = "11 12 16\n"
        elems[19] = "12 16 17\n"
        elems[24] = "15 16 20\n"
        elems[25] = "16 20 21\n"
        material = [0]*7 + [1] + [0]*5 + [1]*3 + [0]*3 + [1]*5 + [0] + [1]*7
        self.check_mesh(tri, elems, coords, material)

    def test_5x5Type2(self):
        tri, elems, coords = self.generate_test_triangle_case(2, 5, 0)
        elems[6] = "3 4 8\n"
        elems[7] = "4 8 9\n"
        elems[12] = "7 8 12\n"
        elems[13] = "8 12 13\n"
        elems[12] = "7 8 12\n"
        elems[18] = "11 12 16\n"
        elems[19] = "12 16 17\n"
        elems[24] = "15 16 20\n"
        elems[25] = "16 20 21\n"
        material = [1]*7 + [0] + [1]*5 + [0]*3 + [1]*3 + [0]*5 + [1] + [0]*7
        self.check_mesh(tri, elems, coords, material)

    def test_5x5Type3(self):
        tri = self.get_triangle(3, 5, 5)
        e, c = self.generate_grid(5, 5)
        m = []
        for i in range(0, 4):
            air = i*2 + 1
            mat = 8 - air
            m = m + [0]*air + [1]*mat
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
        e[8] = '5 6 9\n'  # Type 1 produces distorted grid
        e[9] = '6 9 10\n'
        m = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        self.check_mesh(tri, e, c, m)

    def test_2x2Type1_air2(self):
        air = 2
        tri = self.get_triangle(1, 2, 2, air, air, air, air)
        e, c = self.generate_grid(6, 6)
        e[24] = '14 15 20\n'  # Type 1 produces distorted grid
        e[25] = '15 20 21\n'
        m = [0]*25 + [1] + [0]*24  # one figure element and rest are air
        self.check_mesh(tri, e, c, m)

    def test_2x2Type2_air1(self):
        air = 1
        tri = self.get_triangle(2, 2, 2, air, air, air, air)
        e, c = self.generate_grid(4, 4)
        e[8] = '5 6 9\n'  # Type 2 produces distorted grid
        e[9] = '6 9 10\n'
        m = [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.check_mesh(tri, e, c, m)

    def test_2x2Type2_air2(self):
        air = 2
        tri = self.get_triangle(2, 2, 2, air, air, air, air)
        e, c = self.generate_grid(6, 6)
        e[24] = '14 15 20\n'  # Type 1 produces distorted grid
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
        e[12] = "7 8 12\n"
        e[13] = "8 12 13\n"
        e[18] = "11 12 16\n"
        e[19] = "12 16 17\n"
        m = [0]*13 + [1] + [0]*5 + [1]*3 + [0]*10
        self.check_mesh(tri, e, c, m)

    def test_3x3Type1_air2(self):
        tri, e, c = self.generate_test_triangle_case(1, 3, 2)
        e[30] = "17 18 24\n"
        e[31] = "18 24 25\n"
        e[40] = "23 24 30\n"
        e[41] = "24 30 31\n"
        m = [0] * 31 + [1] + [0]*9 + [1]*3 + [0]*28
        self.check_mesh(tri, e, c, m)

    def test_3x3Type2_air1(self):
        tri, e, c = self.generate_test_triangle_case(2, 3, 1)
        e[12] = "7 8 12\n"
        e[13] = "8 12 13\n"
        e[18] = "11 12 16\n"
        e[19] = "12 16 17\n"
        m = [0] * 10 + [1]*3 + [0]*5 + [1] + [0]*13
        self.check_mesh(tri, e, c, m)

    def test_3x3Type2_air2(self):
        tri, e, c = self.generate_test_triangle_case(2, 3, 2)
        e[30] = "17 18 24\n"
        e[31] = "18 24 25\n"
        e[40] = "23 24 30\n"
        e[41] = "24 30 31\n"
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
    def test_2x2Type0_air1_bareLeft(self):
        air = 1
        dimensions = 2
        tri = self.get_triangle(0, dimensions, dimensions, air, air, air, 0)
        e, c = self.generate_grid(3, 4)
        m = [0]*4 + [1] + [0]*7
        self.check_mesh(tri, e, c, m)

    def test_2x2Type1_air1_bareLeft(self):
        air = 1
        dimensions = 2
        tri = self.get_triangle(1, dimensions, dimensions, air, air, air, 0)
        e, c = self.generate_grid(3, 4)
        e[4] = "3 4 6\n"
        e[5] = "4 6 7\n"
        m = [0]*5 + [1] + [0]*6
        self.check_mesh(tri, e, c, m)

    def test_2x2Type3_air1_bareLeft(self):
        air = 1
        dimensions = 2
        tri = self.get_triangle(3, dimensions, dimensions, air, air, air, 0)
        e, c = self.generate_grid(3, 4)
        m = [0]*5 + [1] + [0]*6
        self.check_mesh(tri, e, c, m)

    def test_2x2Type0_air2_bareLeft(self):
        air = 2
        dimensions = 2
        tri = self.get_triangle(0, dimensions, dimensions, air, air, air, 0)
        e, c = self.generate_grid(4, 6)
        m = [0]*12 + [1] + [0]*17
        self.check_mesh(tri, e, c, m)

    def test_2x2Type3_air2_bareLeft(self):
        air = 2
        dimensions = 2
        tri = self.get_triangle(3, dimensions, dimensions, air, air, air, 0)
        e, c = self.generate_grid(4, 6)
        m = [0]*13 + [1] + [0]*16
        self.check_mesh(tri, e, c, m)

    def test_3x3Type0_air1_bareLeft(self):
        air = 1
        dimensions = 3
        tri = self.get_triangle(0, dimensions, dimensions, air, air, air, 0)
        e, c = self.generate_grid(4, 5)
        m = [0]*6 + [1] + [0]*5 + [1]*3 + [0]*9
        self.check_mesh(tri, e, c, m)

    def test_3x3Type3_air1_bareLeft(self):
        air = 1
        dimensions = 3
        tri = self.get_triangle(3, dimensions, dimensions, air, air, air, 0)
        e, c = self.generate_grid(4, 5)
        m = [0]*7 + [1]*3 + [0]*5 + [1] + [0]*8
        self.check_mesh(tri, e, c, m)

    def test_3x3Type0_air2_bareLeft(self):
        air = 2
        dimensions = 3
        tri = self.get_triangle(0, dimensions, dimensions, air, air, air, 0)
        e, c = self.generate_grid(5, 7)
        m = [0]*16 + [1] + [0]*7 + [1]*3 + [0]*21
        self.check_mesh(tri, e, c, m)

    def test_3x3Type3_air2_bareLeft(self):
        air = 2
        dimensions = 3
        tri = self.get_triangle(3, dimensions, dimensions, air, air, air, 0)
        e, c = self.generate_grid(5, 7)
        m = [0]*17 + [1]*3 + [0]*7 + [1] + [0]*20
        self.check_mesh(tri, e, c, m)


if __name__ == '__main__':
    unittest.main()
