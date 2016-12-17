from PyQt5.QtWidgets import QWidget
from PyQt5 import uic

class Triangle:
    """
    Primitive figure, a rectangle
    """
    def __init__(self, fig, mesh):
        """
        """
        self.binds = [None]*4
        self.modify(fig, mesh)

class NewTriangleWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        uic.loadUi('ui/new_triangle.ui', self)

        self.comboBox.currentIndexChanged.connect(self.select_type)

    def select_type(self, index):
        boxes = [self.air_top, self.air_left, self.air_right, self.air_bottom]
        states = [False, True, False, True]
        if index == 1:
            states = [False, False, True, True]
        if index == 2:
            states = [True, True, False, False]
        if index == 3:
            states = [True, False, True, False]

        for i in range(0, 4):
            boxes[i].setEnabled(states[i])

    def get_data(self):
        pass
