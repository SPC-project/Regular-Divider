import unittest
import sys

from test.AbstractTest import AbstractTest
from PyQt5.QtWidgets import QApplication
app = QApplication(sys.argv)


class Diverse(AbstractTest):
    def test_TLetter_with_toes(self):
        RIGHT, BOTTOM, LEFT = 1, 2, 3
        left_hand = self.get_pos_rectangle(1, 1, 4, 2)
        center_0 = self.get_pos_rectangle(4, 1, 2, 2)
        right_hand = self.get_pos_rectangle(5, 1, 4, 2)
        center_1 = self.get_pos_rectangle(4, 2, 2, 2)
        center_2 = self.get_pos_rectangle(4, 3, 2, 2)
        center_3 = self.get_pos_rectangle(4, 4, 2, 2)
        left_toe = self.get_pos_triangle(3, 4, 1, 2, 2)
        right_toe = self.get_pos_triangle(5, 4, 0, 2, 2)
        left_palm = self.get_pos_triangle(1, 2, 2, 2, 2)
        right_palm = self.get_pos_triangle(7, 2, 3, 2, 2)

        self.fig.adopt_primitive(*left_hand)
        self.expand_fig(0, RIGHT, center_0)
        self.expand_fig(1, RIGHT, right_hand)
        self.expand_fig(1, BOTTOM, center_1)
        self.expand_fig(3, BOTTOM, center_2)
        self.expand_fig(4, BOTTOM, center_3)
        self.expand_fig(5, LEFT, left_toe)
        self.expand_fig(5, RIGHT, right_toe)
        self.expand_fig(0, BOTTOM, left_palm)
        self.expand_fig(2, BOTTOM, right_palm)

        export_test = ['type: rectangle | 1 1 3 1 | 0 0 0 0 3 1\n',
                       'type: rectangle | 4 1 1 1 | 0 0 0 0 1 1\n',
                       'type: rectangle | 5 1 3 1 | 0 0 0 0 3 1\n',
                       'type: rectangle | 4 2 1 1 | 0 0 0 0 1 1\n',
                       'type: rectangle | 4 3 1 1 | 0 0 0 0 1 1\n',
                       'type: rectangle | 4 4 1 1 | 0 0 0 0 1 1\n',
                       'type: triangle | form: 1 | 3 4 1 1 | 0 0 0 0 1 1\n',
                       'type: triangle | form: 0 | 5 4 1 1 | 0 0 0 0 1 1\n',
                       'type: triangle | form: 2 | 1 2 1 1 | 0 0 0 0 1 1\n',
                       'type: triangle | form: 3 | 7 2 1 1 | 0 0 0 0 1 1\n',

                       '# connections\n',
                       '-1 1 8 -1 \n',
                       '-1 2 3 0 \n',
                       '-1 -1 9 1 \n',
                       '1 -1 4 -1 \n',
                       '3 -1 5 -1 \n',
                       '4 7 -1 6 \n',
                       '-1 5 -1 -1 \n',
                       '-1 -1 -1 5 \n',
                       '0 -1 -1 -1 \n',
                       '2 -1 -1 -1 \n']
        self.check_exporting(export_test)

        self.fig.set_air(1)  # Окружим воздушным слоев шириной в единицу
        e = ['0 10 11\n', '0 1 11\n', '1 11 12\n', '1 2 12\n', '2 12 13\n', '2 3 13\n', '3 13 14\n', '3 4 14\n', '4 14 15\n', '4 5 15\n', '5 15 16\n', '5 6 16\n', '6 16 17\n', '6 7 17\n', '7 17 18\n', '7 8 18\n', '8 18 19\n', '8 9 19\n', '10 20 21\n', '10 11 21\n', '11 21 22\n', '11 12 22\n', '12 22 23\n', '12 13 23\n', '13 23 24\n', '13 14 24\n', '14 24 25\n', '14 15 25\n', '15 25 26\n', '15 16 26\n', '16 26 27\n', '16 17 27\n', '17 27 28\n', '17 18 28\n', '18 28 29\n', '18 19 29\n', '20 30 31\n', '20 21 31\n', '21 31 22\n', '22 31 32\n', '22 32 33\n', '22 23 33\n', '23 33 34\n', '23 24 34\n', '24 34 35\n', '24 25 35\n', '25 35 36\n', '25 26 36\n', '26 36 37\n', '26 27 37\n', '27 37 38\n', '27 28 38\n', '28 38 39\n', '28 29 39\n', '30 40 41\n', '30 31 41\n', '31 41 42\n', '31 32 42\n', '32 42 43\n', '32 33 43\n', '33 43 44\n', '33 34 44\n', '34 44 45\n', '34 35 45\n', '35 45 46\n', '35 36 46\n', '36 46 47\n', '36 37 47\n', '37 47 48\n', '37 38 48\n', '38 48 49\n', '38 39 49\n', '42 50 51\n', '42 43 51\n', '43 51 44\n', '44 51 52\n', '44 52 53\n', '44 45 53\n', '45 53 54\n', '45 46 54\n', '46 54 55\n', '46 47 55\n', '50 56 57\n', '50 51 57\n', '51 57 58\n', '51 52 58\n', '52 58 59\n', '52 53 59\n', '53 59 60\n', '53 54 60\n', '54 60 61\n', '54 55 61\n']
        _, c1 = self.generate_grid(10, 5)
        _, c2 = self.generate_grid(6, 2, 0, 2, 5)

        m = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        self.check_figure(e, c1 + c2, m)

    def test_airOnMaterial(self):
        RIGHT, BOTTOM, LEFT = 1, 2, 3

        first = self.get_pos_rectangle(0, 0, 2, 2, 0, 0, 2, 0)
        second = self.get_pos_rectangle(1, 0, 2, 3)
        third = self.get_pos_rectangle(1, 2, 2, 2)
        forth = self.get_pos_rectangle(0, 2, 2, 2)

        self.fig.adopt_primitive(*first)
        self.expand_fig(0, RIGHT, second)
        self.expand_fig(1, BOTTOM, third)
        self.expand_fig(2, LEFT, forth)

        elems = ['0 3 4\n', '0 1 4\n', '1 4 5\n', '1 2 5\n', '3 6 7\n', '3 4 7\n', '4 7 8\n', '4 5 8\n', '6 9 10\n', '6 7 10\n', '7 10 11\n', '7 8 11\n']
        coords = list()
        for j in range(4):
            for i in range(3):
                coords.append([i, j])
        material = [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1]

        self.check_figure(elems, coords, material)


if __name__ == '__main__':
    unittest.main()
