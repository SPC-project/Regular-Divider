import unittest
import sys
import os

from test.abstractTest import AbstractTest
from src.gui_primitive import NewRectangleWidget
from PyQt5.QtWidgets import QApplication
app = QApplication(sys.argv)

class TestSoloTriangleMesh(AbstractTest):
    def test_4x4TriangleType0_withRectangle_singleAirLayer(self):
        tri = self.get_triangle(0, 4, 4, 1, 1, 3, 0)

        self.fig.adopt_primitive(*tri)

        widget = NewRectangleWidget()
        widget.for_expanding(self.fig.shape[0], 3)  # expand at left side
        widget.width.setValue(3.0)
        widget.Nx.setValue(4)
        widget.air_top.setValue(1)
        fig, mesh = widget.get_data()
        self.fig.adopt_primitive(fig, mesh, 0)  # '0' for Rectangle

        # Combine primitives
        first = self.fig.shape[0]
        expanded = self.fig.shape[1]
        first.connect(3, expanded)
        expanded.connect(1, first)

        self.fig.save_mesh()

        elems_test = None
        coords_test = None


if __name__ == '__main__':
    unittest.main()
