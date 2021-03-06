import unittest
import sys

from test.AbstractTest import AbstractTest
from PyQt5.QtWidgets import QApplication
app = QApplication(sys.argv)


class NoAir(AbstractTest):
    """
    Check how meshing work on pure-Figure rectangles

    'self.get_rectangle(nx, ny)' generates pair (box, mesh), that is used by
        'self.check_mesh' for creating and meshing the figure
    Variables 'e', 'c' and 'm' store expected result for meshing
    """
    def test_2x2(self):
        rect = self.get_rectangle(2, 2)
        e, c = self.generate_grid(2, 2)
        m = [1, 1]
        self.check_mesh(rect, e, c, m)

    def test_3x3(self):
        rect = self.get_rectangle(3, 3)
        e, c = self.generate_grid(3, 3)
        m = [1, 1, 1, 1, 1, 1, 1, 1]
        self.check_mesh(rect, e, c, m)

    def test_4x4(self):
        rect = self.get_rectangle(4, 4)
        e, c = self.generate_grid(4, 4)
        m = [1] * 18
        self.check_mesh(rect, e, c, m)


class UpperAir(AbstractTest):
    """
    Check how meshing work with triangles just
    """
    def test_2x2(self):
        rect = self.get_rectangle(2, 2, top=1)
        e, c = self.generate_grid(2, 3)
        m = [0, 0, 1, 1]
        self.check_mesh(rect, e, c, m)

    def test_3x3(self):
        rect = self.get_rectangle(3, 3, top=1)
        e, c = self.generate_grid(3, 4)
        m = [0]*4 + [1]*8
        self.check_mesh(rect, e, c, m)

    def test_4x4(self):
        rect = self.get_rectangle(4, 4, top=1)
        e, c = self.generate_grid(4, 5)
        m = [0]*6 + [1]*18
        self.check_mesh(rect, e, c, m)

    def test_4x4_2(self):
        rect = self.get_rectangle(4, 4, top=2)
        e, c = self.generate_grid(4, 6)
        m = [0]*12 + [1]*18
        self.check_mesh(rect, e, c, m)


class RightAir(AbstractTest):
    def test_2x2(self):
        rect = self.get_rectangle(2, 2, right=1)
        e, c = self.generate_grid(3, 2)
        m = [1, 1, 0, 0]
        self.check_mesh(rect, e, c, m)

    def test_3x3(self):
        rect = self.get_rectangle(3, 3, right=1)
        e, c = self.generate_grid(4, 3)
        m = [1, 1, 1, 1] + [0, 0] + [1, 1, 1, 1] + [0, 0]
        self.check_mesh(rect, e, c, m)

    def test_4x4(self):
        rect = self.get_rectangle(4, 4, right=1)
        e, c = self.generate_grid(5, 4)
        m = [1]*6 + [0]*2 + [1]*6 + [0]*2 + [1]*6 + [0]*2
        self.check_mesh(rect, e, c, m)

    def test_4x4_2(self):
        rect = self.get_rectangle(4, 4, right=2)
        e, c = self.generate_grid(6, 4)
        m = [1]*6 + [0]*4 + [1]*6 + [0]*4 + [1]*6 + [0]*4
        self.check_mesh(rect, e, c, m)


class BottomAir(AbstractTest):
    def test_2x2(self):
        rect = self.get_rectangle(2, 2, bottom=1)
        e, c = self.generate_grid(2, 3)
        m = [1, 1, 0, 0]
        self.check_mesh(rect, e, c, m)

    def test_3x3(self):
        rect = self.get_rectangle(3, 3, bottom=1)
        e, c = self.generate_grid(3, 4)
        m = [1]*8 + [0]*4
        self.check_mesh(rect, e, c, m)

    def test_4x4(self):
        rect = self.get_rectangle(4, 4, bottom=1)
        e, c = self.generate_grid(4, 5)
        m = [1]*18 + [0]*6
        self.check_mesh(rect, e, c, m)

    def test_4x4_2(self):
        rect = self.get_rectangle(4, 4, bottom=2)
        e, c = self.generate_grid(4, 6)
        m = [1]*18 + [0]*12
        self.check_mesh(rect, e, c, m)


class LeftAir(AbstractTest):
    def test_2x2(self):
        rect = self.get_rectangle(2, 2, left=1)
        e, c = self.generate_grid(3, 2)
        m = [0, 0, 1, 1]
        self.check_mesh(rect, e, c, m)

    def test_3x3(self):
        rect = self.get_rectangle(3, 3, left=1)
        e, c = self.generate_grid(4, 3)
        m = [0, 0] + [1, 1, 1, 1] + [0, 0] + [1, 1, 1, 1]
        self.check_mesh(rect, e, c, m)

    def test_4x4(self):
        rect = self.get_rectangle(4, 4, left=1)
        e, c = self.generate_grid(5, 4)
        m = [0]*2 + [1]*6 + [0]*2 + [1]*6 + [0]*2 + [1]*6
        self.check_mesh(rect, e, c, m)

    def test_4x4_2(self):
        rect = self.get_rectangle(4, 4, left=2)
        e, c = self.generate_grid(6, 4)
        m = [0]*4 + [1]*6 + [0]*4 + [1]*6 + [0]*4 + [1]*6
        self.check_mesh(rect, e, c, m)


class TwoAir(AbstractTest):
    def test_2x2_air1_topRight(self):
        self.generate_testCase_rectangle(2, 1, 1, 0, 0)

    def test_2x2_air1_topBottom(self):
        self.generate_testCase_rectangle(2, 1, 0, 1, 0)

    def test_2x2_air1_topLeft(self):
        self.generate_testCase_rectangle(2, 1, 0, 0, 1)

    def test_2x2_air1_rightBottom(self):
        self.generate_testCase_rectangle(2, 0, 1, 1, 0)

    def test_2x2_air1_rightLeft(self):
        self.generate_testCase_rectangle(2, 0, 1, 0, 1)

    def test_2x2_air1_bottomLeft(self):
        self.generate_testCase_rectangle(2, 0, 0, 1, 1)

    def test_2x2_air2_topRight(self):
        self.generate_testCase_rectangle(2, 1, 1, 0, 0, air=2)

    def test_2x2_air2_topBottom(self):
        self.generate_testCase_rectangle(2, 1, 0, 1, 0, air=2)

    def test_2x2_air2_topLeft(self):
        self.generate_testCase_rectangle(2, 1, 0, 0, 1, air=2)

    def test_2x2_air2_rightBottom(self):
        self.generate_testCase_rectangle(2, 0, 1, 1, 0, air=2)

    def test_2x2_air2_rightLeft(self):
        self.generate_testCase_rectangle(2, 0, 1, 0, 1, air=2)

    def test_2x2_air2_bottomLeft(self):
        self.generate_testCase_rectangle(2, 0, 0, 1, 1, air=2)

    def test_3x3_air1_topRight(self):
        self.generate_testCase_rectangle(3, 1, 1, 0, 0)

    def test_3x3_air1_topBottom(self):
        self.generate_testCase_rectangle(3, 1, 0, 1, 0)

    def test_3x3_air1_topLeft(self):
        self.generate_testCase_rectangle(3, 1, 0, 0, 1)

    def test_3x3_air1_rightBottom(self):
        self.generate_testCase_rectangle(3, 0, 1, 1, 0)

    def test_3x3_air1_rightLeft(self):
        self.generate_testCase_rectangle(3, 0, 1, 0, 1)

    def test_3x3_air1_bottomLeft(self):
        self.generate_testCase_rectangle(3, 0, 0, 1, 1)

    def test_3x3_air2_topRight(self):
        self.generate_testCase_rectangle(3, 1, 1, 0, 0, air=2)

    def test_3x3_air2_topBottom(self):
        self.generate_testCase_rectangle(3, 1, 0, 1, 0, air=2)

    def test_3x3_air2_topLeft(self):
        self.generate_testCase_rectangle(3, 1, 0, 0, 1, air=2)

    def test_3x3_air2_rightBottom(self):
        self.generate_testCase_rectangle(3, 0, 1, 1, 0, air=2)

    def test_3x3_air2_rightLeft(self):
        self.generate_testCase_rectangle(3, 0, 1, 0, 1, air=2)

    def test_3x3_air2_bottomLeft(self):
        self.generate_testCase_rectangle(3, 0, 0, 1, 1, air=2)


class ThreeAir(AbstractTest):
    def test_2x2_air1_topRightBottom(self):
        self.generate_testCase_rectangle(2, 1, 1, 1, 0)

    def test_2x2_air1_topRightLeft(self):
        self.generate_testCase_rectangle(2, 1, 1, 0, 1)

    def test_2x2_air1_TopBottomLeft(self):
        self.generate_testCase_rectangle(2, 1, 0, 1, 1)

    def test_2x2_air1_RightBottomLeft(self):
        self.generate_testCase_rectangle(2, 0, 1, 1, 1)

    def test_3x3_air1_topRightBottom(self):
        self.generate_testCase_rectangle(2, 1, 1, 1, 0)

    def test_3x3_air1_topRightLeft(self):
        self.generate_testCase_rectangle(2, 1, 1, 0, 1)

    def test_3x3_air1_TopBottomLeft(self):
        self.generate_testCase_rectangle(2, 1, 0, 1, 1)

    def test_3x3_air1_RightBottomLeft(self):
        self.generate_testCase_rectangle(2, 0, 1, 1, 1)

    def test_2x2_air2_topRightBottom(self):
        self.generate_testCase_rectangle(2, 1, 1, 1, 0, air=2)

    def test_2x2_air2_topRightLeft(self):
        self.generate_testCase_rectangle(2, 1, 1, 0, 1, air=2)
    def test_2x2_air2_TopBottomLeft(self):
        self.generate_testCase_rectangle(2, 1, 0, 1, 1, air=2)
    def test_2x2_air2_RightBottomLeft(self):
        self.generate_testCase_rectangle(2, 0, 1, 1, 1, air=2)
    def test_3x3_air2_topRightBottom(self):
        self.generate_testCase_rectangle(2, 1, 1, 1, 0, air=2)
    def test_3x3_air2_topRightLeft(self):
        self.generate_testCase_rectangle(2, 1, 1, 0, 1, air=2)
    def test_3x3_air2_TopBottomLeft(self):
        self.generate_testCase_rectangle(2, 1, 0, 1, 1, air=2)
    def test_3x3_air2_RightBottomLeft(self):
        self.generate_testCase_rectangle(2, 0, 1, 1, 1)


class FullAir(AbstractTest):
    def test_2x2_1(self):
        rect = self.get_rectangle(2, 2, 1, 1, 1, 1)
        e, c = self.generate_grid(4, 4)
        m = [0]*6 + [0]*2 + [1]*2 + [0]*2 + [0]*6
        self.check_mesh(rect, e, c, m)

    def test_2x2_2(self):
        air = 2
        rect = self.get_rectangle(2, 2, air, air, air, air)
        e, c = self.generate_grid(6, 6)
        m = [0]*20 + [0]*4 + [1]*2 + [0]*4 + [0]*20
        self.check_mesh(rect, e, c, m)

    def test_3x3_1(self):
        air = 1
        rect = self.get_rectangle(3, 3, air, air, air, air)
        e, c = self.generate_grid(5, 5)
        m = [0]*8 + [0]*2 + [1]*4 + [0]*2 + [0]*2 + [1]*4 + [0]*2 + [0]*8
        self.check_mesh(rect, e, c, m)

    def test_3x3_2(self):
        air = 2
        rect = self.get_rectangle(3, 3, air, air, air, air)
        e, c = self.generate_grid(7, 7)
        m = [0]*24 + [0]*4 + [1]*4 + [0]*4 + [0]*4 + [1]*4 + [0]*4 + [0]*24
        self.check_mesh(rect, e, c, m)

    def test_4x4_1(self):
        air = 1
        rect = self.get_rectangle(4, 4, air, air, air, air)
        e, c = self.generate_grid(6, 6)
        m = [0]*10 + [0]*2 + [1]*6 + [0]*2 + [0]*2 + [1]*6 + [0]*2 + [0]*2 + [1]*6 + [0]*2 + [0]*10
        self.check_mesh(rect, e, c, m)

    def test_4x4_2(self):
        air = 2
        rect = self.get_rectangle(4, 4, air, air, air, air)
        e, c = self.generate_grid(8, 8)
        layer = [0]*4 + [1]*6 + [0]*4
        m = [0]*28 + layer + layer + layer + [0]*28
        self.check_mesh(rect, e, c, m)


if __name__ == '__main__':
    unittest.main()
