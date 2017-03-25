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


class TestSoloRectangleMesh(unittest.TestCase):
    def setUp(self):
        holder = FakeParentApp()
        self.fig = Figure(holder, holder, holder, holder)
        self.fig.world_size = 10
        self.fig.start_x = 0
        self.fig.start_y = 0

    def get_type1(self, top=0, right=0, bottom=0, left=0):
        box = (0.5, 0.5, 2, 2)  # x, y, w, h
        nodes = [top, right, bottom, left, 1, 1]
        other_data = {'type': 'rectangle'}
        mesh = Mesh(nodes, other_data)

        return box, mesh, 0  # '0' for Rectangle

    def get_type2(self):
        box = (0.5, 0.5, 2, 2)  # x, y, w, h
        nodes = [0, 0, 0, 0, 2, 2]  # Air: top, right, down, left, Figure: x, y
        other_data = {'type': 'rectangle'}
        mesh = Mesh(nodes, other_data)

        return box, mesh, 0  # '0' for Rectangle

    def get_type3(self):
        box = (0.5, 0.5, 2, 2)  # x, y, w, h
        nodes = [0, 0, 0, 0, 3, 3]  # Air: top, right, down, left, Figure: x, y
        other_data = {'type': 'rectangle'}
        mesh = Mesh(nodes, other_data)

        return box, mesh, 0  # '0' for Rectangle

    def test_noAirTwoElementsExportImport(self):
        self.fig.adopt_primitive(*self.get_type1())

        filename = "./test/check_rectangle.d40do"
        self.fig.exporting(filename)
        self.fig.importing(filename)
        self.assertEqual(len(self.fig.shape), 1, "Should be exactly one primitive")

        type_ = self.fig.shape[0].mesh.data["type"]
        self.assertEqual(type_, "rectangle", "Type should be rectangle")
        os.remove(filename)

    def check_mesh(self, input, data, name):
        """
        data — список элементов, что будут образованы разбиением. Элемент задается индексами трёх формирующих его вершин
        """
        self.fig.adopt_primitive(*input)
        filename = "./test/check_rectangle.pmd"
        self.fig.save_mesh(filename)

        with open(Output.TEMP_DIR + Output.FILENAMES[0] + ".tmp", "r") as f:
            triangles = f.readlines()
            self.assertEqual(triangles, data, "Wrong triangles formed for: " + name)

        # os.remove(filename)

    def test_noAirTwoElementsSave(self):
        elements_example = ['0 2 3\n', '0 1 3\n']
        self.check_mesh(self.get_type1(), elements_example, "2x2 grid")

    def test_noAirFourElementsSave(self):
        elements_example = ['0 3 4\n', '0 1 4\n', '1 4 5\n', '1 2 5\n',
                            '3 6 7\n', '3 4 7\n', '4 7 8\n', '4 5 8\n']
        self.check_mesh(self.get_type2(), elements_example, "3x3 grid")

    def test_noAirNineElementsSave(self):
        elements_example = [
        '0 4 5\n',   '0 1 5\n',  '1 5 6\n',   '1 2 6\n',   '2 6 7\n',    '2 3 7\n',
        '4 8 9\n',   '4 5 9\n',  '5 9 10\n',  '5 6 10\n',  '6 10 11\n',  '6 7 11\n',
        '8 12 13\n', '8 9 13\n', '9 13 14\n', '9 10 14\n', '10 14 15\n', '10 11 15\n']
        self.check_mesh(self.get_type3(), elements_example, "4x4 grid")

    def test_airUpTwoElements(self):
        elements_example = ['0 2 3\n', '0 1 3\n', '2 4 5\n', '2 3 5\n',
                            '4 6 7\n', '4 5 7\n']
        self.check_mesh(self.get_type1(2), elements_example, "4x2 grid, 2x2 figure")


if __name__ == '__main__':
    unittest.main()
