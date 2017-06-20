import unittest
from src.primitive import Mesh
from test.AbstractTest import AbstractTest


class FakeOutput:
    def __init__(self):
        self.res = list()

    def write(self, line):
        self.res.append(line)


class FakeInput:
    def __init__(self, data_):
        self.data = data_

    def readlines(self):
        return self.data


class ElementsOverlay(unittest.TestCase):
    pass


class ElementsReindexing(unittest.TestCase):
    pass


class ExcessiveNodes(AbstractTest):
    def test_precision_problem(self):
        """
        Coordinates for that rectangle will be periodical — so, can't be compared by machine.
        In Output.save_nodes we sat only 4 digits after coma, it solve the problem
        """
        box = (0, 0, 4, 4)  # x, y, w, h
        nodes = [2, 2, 2, 2, 3, 3]  # Four air layers and two parameters for figure's grid
        other_data = {'type': 'rectangle'}
        mesh = Mesh(nodes, other_data)
        rect = (box, mesh, 0)  # '0' for Rectangle

        nx, ny = 8, 8  # width&height off all grid
        e = list()
        for j in range(ny-1):
            for i in range(nx-1):
                curr = i + (nx*j)
                next_ = curr + 1
                next_line_curr = curr + nx
                next_line_next = next_line_curr + 1
                e.append("{} {} {}\n".format(curr, next_line_curr, next_line_next))
                e.append("{} {} {}\n".format(curr, next_, next_line_next))

        c = list()
        for j in range(ny):
            y = round(-2.66666666666 + j*1.33333333333, 4)
            for i in range(nx):
                x = round(-2.66666666666 + i*1.33333333333, 4)
                c.append([x, y])

        layer = [0]*4 + [1]*6 + [0]*4
        m = [0]*28 + layer + layer + layer + [0]*28
        self.check_mesh(rect, e, c, m)

if __name__ == '__main__':
    unittest.main()
