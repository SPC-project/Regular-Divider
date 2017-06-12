import unittest
from Combiner import write_elements


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
    def test_wrongAtEnd(self):
        elems_test = ['3 6 7\n', '3 4 7\n', '0 3 4\n', '0 1 4\n',
                      '4 7 8\n', '4 5 8\n', '1 4 5\n', '1 2 5\n',
                      '4 7 8\n', '4 5 8\n', '1 4 5\n', '1 2 5\n']

        out = FakeOutput()
        in_ = FakeInput(elems_test)
        excessive = write_elements(out, in_, [])
        unspoiled_elems = elems_test[:-4]

        self.assertEqual(out.res, unspoiled_elems)
        self.assertEqual(excessive, [8, 9, 10, 11])

    def test_wrongAtMiddle(self):
        elems_test = ['3 6 7\n', '3 4 7\n', '0 3 4\n', '0 1 4\n',
                      '3 6 7\n', '3 4 7\n', '0 3 4\n', '0 1 4\n',
                      '4 7 8\n', '4 5 8\n', '1 4 5\n', '1 2 5\n']

        out = FakeOutput()
        in_ = FakeInput(elems_test)
        excessive = write_elements(out, in_, [])
        unspoiled_elems = elems_test[:4] + elems_test[8:]

        self.assertEqual(out.res, unspoiled_elems)
        self.assertEqual(excessive, [4, 5, 6, 7])

    def test_wrongEveryNext(self):
        elems_correct = ['3 6 7\n', '3 4 7\n', '0 3 4\n', '0 1 4\n',
                         '4 7 8\n', '4 5 8\n', '1 4 5\n', '1 2 5\n']
        elems_wrong = ['3 6 7\n', '3 6 7\n', '3 4 7\n', '3 4 7\n',
                       '0 3 4\n', '0 3 4\n', '0 1 4\n', '0 1 4\n',
                       '4 7 8\n', '4 7 8\n', '4 5 8\n', '4 5 8\n',
                       '1 4 5\n', '1 4 5\n', '1 2 5\n', '1 2 5\n']

        out = FakeOutput()
        in_ = FakeInput(elems_wrong)
        excessive = write_elements(out, in_, [])

        self.assertEqual(out.res, elems_correct)
        self.assertEqual(excessive, [1, 3, 5, 7, 9, 11, 13, 15])

    def test_airOnMaterial(self):
        elems = ['3 6 7\n', '3 4 7\n', '6 9 10\n', '6 7 10\n', '0 3 4\n', '0 1 4\n', '1 4 5\n', '1 2 5\n', '4 7 8\n', '4 5 8\n', '7 10 11\n', '7 8 11\n']
        coords = list()
        for j in range(5):
            for i in range(3):
                coords.append([i, j])
        material = [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

        out = FakeOutput()
        in_ = FakeInput(elems)
        excessive = write_elements(out, in_, [])
        self.assertEqual(excessive, [1, 3, 5, 7, 9, 11, 13, 15])


class ElementsReindexing(unittest.TestCase):
    def test_f(self):
        pass


class ExcessiveNodes(unittest.TestCase):
    def test_f(self):
        pass


if __name__ == '__main__':
    unittest.main()
