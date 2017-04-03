import unittest
import sys
import os

from test.abstractTest import AbstractTest
from PyQt5.QtWidgets import QApplication
app = QApplication(sys.argv)


class Test_Rectangle(AbstractTest):
    def test_2x2_noAir_ExportImport(self):
        self.fig.adopt_primitive(*self.get_rectangle(2, 2))

        filename = "./test/check_rectangle.d40do"
        self.fig.exporting(filename)
        self.fig.importing(filename)
        self.assertEqual(len(self.fig.shape), 1, "Should be exactly one primitive")

        type_ = self.fig.shape[0].mesh.data["type"]
        self.assertEqual(type_, "rectangle", "Type should be rectangle")
        os.remove(filename)

    def test_3x3_noAir(self):
        rect = self.get_rectangle(3, 3)
        elems_test = ['0 3 4\n', '0 1 4\n', '1 4 5\n', '1 2 5\n',
                      '3 6 7\n', '3 4 7\n', '4 7 8\n', '4 5 8\n']
        coords_test = [[0.0, 0.0], [1.0, 0.0], [2.0, 0.0], [0.0, 1.0], [1.0, 1.0], [2.0, 1.0], [0.0, 2.0], [1.0, 2.0], [2.0, 2.0]]
        self.check_mesh(rect, elems_test, coords_test)

    def test_3x3_upperAir(self):
        rect = self.get_rectangle(3, 3, 1)
        elems_test = ['0 3 4\n', '0 1 4\n', '1 4 5\n', '1 2 5\n', '6 9 10\n', '6 7 10\n', '7 10 11\n', '7 8 11\n', '9 12 13\n', '9 10 13\n', '10 13 14\n', '10 11 14\n']
        coords_test = [[0.0, 0.0], [1.0, 0.0], [2.0, 0.0], [0.0, 1.0], [1.0, 1.0], [2.0, 1.0], [0.0, 1.0], [1.0, 1.0], [2.0, 1.0], [0.0, 2.0], [1.0, 2.0], [2.0, 2.0], [0.0, 3.0], [1.0, 3.0], [2.0, 3.0]]
        self.check_mesh(rect, elems_test, coords_test)


if __name__ == '__main__':
    unittest.main()
