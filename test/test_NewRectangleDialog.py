import unittest
from PyQt5.QtWidgets import QApplication
from rectangle import Rectangle, NewRectangleDialog


class TestDialog(unittest.TestCase):
    def setUp(self):
        self. app = QApplication(list(''))

    def test_expanding(self):
        fig = (5, 6, 7, 8)
        mesh = [1, 2, 3, 4, 5, 6]
        rect = Rectangle(fig, mesh)
        dialog = NewRectangleDialog()
        dialog.for_expanding(rect, 0)
        print(dialog.get_data())
