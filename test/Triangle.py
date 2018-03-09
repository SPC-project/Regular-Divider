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
        self.generate_testCase_triangle(3, 1, 0, 0, 0, 0)

    def test_3x3Type2(self):
        self.generate_testCase_triangle(3, 2, 0, 0, 0, 0)

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
        self.generate_testCase_triangle(4, 1, 0, 0, 0, 0)

    def test_4x4Type2(self):
        self.generate_testCase_triangle(4, 2, 0, 0, 0, 0)

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
        self.generate_testCase_triangle(5, 1, 0, 0, 0, 0)

    def test_5x5Type2(self):
        self.generate_testCase_triangle(5, 2, 0, 0, 0, 0)

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
        self.generate_testCase_triangle(2, 0, 1, 1, 1, 1)

    def test_2x2Type1_air1(self):
        self.generate_testCase_triangle(2, 0, 1, 1, 1, 1)

    def test_2x2Type2_air1(self):
        self.generate_testCase_triangle(2, 2, 1, 1, 1, 1)

    def test_2x2Type3_air1(self):
        self.generate_testCase_triangle(2, 3, 1, 1, 1, 1)

    def test_2x2Type0_air2(self):
        self.generate_testCase_triangle(2, 0, 2, 2, 2, 2)

    def test_2x2Type1_air2(self):
        self.generate_testCase_triangle(2, 1, 2, 2, 2, 2)

    def test_2x2Type2_air2(self):
        self.generate_testCase_triangle(2, 2, 2, 2, 2, 2)

    def test_2x2Type3_air2(self):
        self.generate_testCase_triangle(2, 3, 2, 2, 2, 2)


class AirCoat(AbstractTest):
    """ Test case for primitive with a full air surrounding """
    def test_3x3Type0_air1(self):
        self.generate_testCase_triangle(3, 0, 1, 1, 1, 1)

    def test_3x3Type1_air1(self):
        self.generate_testCase_triangle(3, 1, 1, 1, 1, 1)

    def test_3x3Type2_air1(self):
        self.generate_testCase_triangle(3, 2, 1, 1, 1, 1)

    def test_3x3Type3_air1(self):
        self.generate_testCase_triangle(3, 3, 1, 1, 1, 1)

    def test_3x3Type0_air2(self):
        self.generate_testCase_triangle(0, 3, 1, 1, 1, 1, air=2)

    def test_3x3Type1_air2(self):
        self.generate_testCase_triangle(1, 3, 1, 1, 1, 1, air=2)

    def test_3x3Type2_air2(self):
        self.generate_testCase_triangle(3, 2, 1, 1, 1, 1, air=2)

    def test_3x3Type3_air2(self):
        self.generate_testCase_triangle(3, 3, 1, 1, 1, 1, air=2)


class OneBareSide(AbstractTest):
    def test_bareTop(self):
        for N in range(2, 4):
            for type_ in range(0, 4):
                for air in range(1, 3):
                    try:
                        self.generate_testCase_triangle(N, type_, 0, 1, 1, 1, air)
                        self.fig.clean()
                    except AssertionError:
                        print("Test failed on triangle with parameters:")
                        print("\t{}x{} | type: {} | air: bare top | air_thickness: {}".format(N, N, type_, air))
                        raise

    def test_bareRight(self):
        for N in range(2, 4):
            for type_ in range(0, 4):
                for air in range(1, 3):
                    try:
                        self.generate_testCase_triangle(N, type_, 1, 0, 1, 1, air)
                        self.fig.clean()
                    except AssertionError:
                        print("Test failed on triangle with parameters:")
                        print("\t{}x{} | type: {} | air: bare right | air_thickness: {}".format(N, N, type_, air))
                        raise

    def test_bareBottom(self):
        for N in range(2, 4):
            for type_ in range(0, 4):
                for air in range(1, 3):
                    try:
                        self.generate_testCase_triangle(N, type_, 1, 1, 0, 1, air)
                        self.fig.clean()
                    except AssertionError:
                        print("Test failed on triangle with parameters:")
                        print("\t{}x{} | type: {} | air: bare bottom | air_thickness: {}".format(N, N, type_, air))
                        raise

    def test_bareLeft(self):
        for N in range(2, 4):
            for type_ in range(0, 4):
                for air in range(1, 3):
                    try:
                        self.generate_testCase_triangle(N, type_, 1, 1, 1, 0, air)
                        self.fig.clean()
                    except AssertionError:
                        print("Test failed on triangle with parameters:")
                        print("\t{}x{} | type: {} | air: bare left | air_thickness: {}".format(N, N, type_, air))
                        raise


if __name__ == '__main__':
    unittest.main()
