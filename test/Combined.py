import unittest
import sys

from test.AbstractTest import AbstractTest
from PyQt5.QtWidgets import QApplication
app = QApplication(sys.argv)


class Diverse(AbstractTest):
    pass


if __name__ == '__main__':
    unittest.main()
