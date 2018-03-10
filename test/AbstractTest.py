import unittest

from src.figure import Figure
from src.primitive import Mesh
from src.displayer import read_pmd, TEMP_DIR
import os

OUTPUT_FILENAME = TEMP_DIR + "/test.pmd"
EXPORT_OUTPUT_FILENAME = TEMP_DIR + "/test.d42do"


class FakeParentApp:
    def setText(self, txt):
        pass

    def adjustSize(self):
        pass

    def emit(self):
        pass


class AbstractTest(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)

        holder = FakeParentApp()
        self.fig = Figure(holder, holder, holder, holder)
        self.fig.world_size = 10
        self.fig.start_x = 0
        self.fig.start_y = 0

    def get_rectangle(self, nx, ny, top=0, right=0, bottom=0, left=0):
        """nx, ny – amount of nodes by OX and OY axes"""
        box = (left, top, nx-1, ny-1)  # x, y, w, h

        # Во внутреннем представлении используются квадраты, а не узлы
        nodes = [top, right, bottom, left, nx-1, ny-1]

        other_data = {'type': 'rectangle'}
        mesh = Mesh(nodes, other_data)

        return box, mesh, 0  # '0' for Rectangle

    def get_pos_rectangle(self, x, y, nx, ny, top=0, right=0, bottom=0, left=0):
        box = (x, y, nx-1, ny-1)  # x, y, w, h
        nodes = [top, right, bottom, left, nx-1, ny-1]
        other_data = {'type': 'rectangle'}
        mesh = Mesh(nodes, other_data)

        return box, mesh, 0  # '0' for Rectangle

    def get_triangle(self, form, nx=2, ny=2, top=0, right=0, bottom=0, left=0):
        box = (left, top, nx-1, ny-1)  # x, y, w, h
        # air: top, right, bottom, left; figure 'squares': by x, by y
        nodes = [top, right, bottom, left, nx-1, ny-1]

        other_data = {'type': 'triangle', 'form': form}
        mesh = Mesh(nodes, other_data)

        return box, mesh, 1  # '1' for Triangle

    def generate_testCase_rectangle(self, N, flag_top, flag_right, flag_bottom, flag_left, air=1):
        """
        Parameters:
            - N – size of rectangle (in nodes)
            - flag_* – '1' if there are air on this side, '0' if not
            - air – how thick is air layer
        """
        air_top = air*flag_top
        air_right = air*flag_right
        air_bottom = air*flag_bottom
        air_left = air*flag_left
        rect = self.get_rectangle(N, N, air_top, air_right, air_bottom, air_left)
        e, c = self.generate_grid(air_left + N + air_right, air_top + N + air_bottom)

        N -= 1  # switch to length in elements (2x2 grid produces two elements)
        material = []
        row_len = (air_left + N + air_right)*2
        for j in range(0, air_top):
            material += [0]*row_len
        for j in range(0, N):
            material += [0]*air_left*2 + [1]*N*2 + [0]*air_right*2
        for j in range(0, air_bottom):
            material += [0]*row_len

        # print(material)
        self.check_mesh(rect, e, c, material)

    def generate_testCase_triangle(self, N, type_, flag_top, flag_right, flag_bottom, flag_left, air=1):
        """
        Parameters:
            - N – length (in nodes) of the triangle's catheti
            - flag_* – '1' if there are air on this side, '0' if not
            - air – how thick is air layer
        """
        air_top = air*flag_top
        air_right = air*flag_right
        air_bottom = air*flag_bottom
        air_left = air*flag_left

        triangle = self.get_triangle(type_, N, N, air_top, air_right, air_bottom, air_left)
        e, c = self.generate_grid(air_left + N + air_right, air_top + N + air_bottom)
        if type_ == 1 or type_ == 2:
            self.distort_grid(e, N, air_top, air_right, air_bottom, air_left)

        material = self.generate_material(N, type_, air_top, air_right, air_bottom, air_left)

        self.check_mesh(triangle, e, c, material)

    def generate_material(self, N, type_, air_top, air_right, air_bottom, air_left):
        N -= 1  # switch to length in elements (2x2 grid produces two elements)
        material = []
        row_len = (air_left + N + air_right)*2
        for j in range(0, air_top):
            material += [0]*row_len

        for j in range(0, N):
            if type_ == 0:
                figure = j*2 + 1  # How much figure's elements is in this row
                material += [0]*air_left*2
                material += [1]*figure
                material += [0]*(air_right*2 + (N*2 - figure))
            elif type_ == 1:
                figure = j*2 + 1  # How much figure's elements is in this row
                material += [0]*(air_left*2 + (N*2 - figure))
                material += [1]*figure
                material += [0]*air_right*2
            elif type_ == 2:
                figure = (N-j)*2 - 1  # How much figure's elements is in this row
                material += [0]*air_left*2
                material += [1]*figure
                material += [0]*(air_right*2 + (N*2 - figure))
            elif type_ == 3:
                figure = (N-j)*2 - 1  # How much figure's elements is in this row
                material += [0]*(air_left*2 + (N*2 - figure))
                material += [1]*figure
                material += [0]*air_right*2
            else:
                raise Exception("Got wrong triangle (type:{})".format(type_))
        for j in range(0, air_bottom):
            material += [0]*row_len

        return material

    def get_pos_triangle(self, x, y, form, nx=2, ny=2, top=0, right=0, bottom=0, left=0):
        box = (x, y, nx-1, ny-1)  # x, y, w, h
        nodes = [top, right, bottom, left, nx-1, ny-1]
        other_data = {'type': 'triangle', 'form': form}
        mesh = Mesh(nodes, other_data)

        return box, mesh, 1  # '1' for Triangle

    def expand_fig(self, ind, side_code, new_data):
        prim = self.fig.shape[ind]
        self.fig.adopt_primitive(*new_data)
        new_prim = self.fig.shape[-1]
        prim.connect(side_code, new_prim)
        new_prim.connect((side_code+2) % 4, prim)  # shave opposite side

    def check_mesh(self, input, elems_test, coords_test, material_test):
        self.fig.adopt_primitive(*input)
        self.check_figure(elems_test, coords_test, material_test)

    def check_figure(self, elems_test, coords_test, material_test):
        """
        elements_test — список элементов, что будут образованы разбиением. Элемент задается индексами трёх формирующих его вершин
        coords_test — список координат узлов. Индекс узла указан третьим числом в строке
        """
        self.fig.save_mesh(OUTPUT_FILENAME, sortElements=True, testing=True)
        self.check_output(elems_test, coords_test, material_test)

    def check_output(self, elems_test, coords_test, material_test):
        with open(OUTPUT_FILENAME, 'r') as Input:
            elements, coordinates, material = read_pmd(Input)
            # print(elements)
            self.assertEqual(elements, elems_test, "Wrong triangles formed for")
            # print(coordinates)
            self.assertEqual(coordinates, coords_test, "Wrong coordinates")
            # print(material)
            self.assertEqual(material, material_test, "Wrong material")

    def check_exporting(self, compare):
        self.fig.exporting(EXPORT_OUTPUT_FILENAME)
        with open(EXPORT_OUTPUT_FILENAME, "r") as exported:
            self.assertEqual(exported.readlines(), compare, "Figure build unexpected")

    def generate_grid(self, nx, ny, offset_index=0, offset_x=0, offset_y=0):
        elems = list()
        for j in range(ny-1):
            for i in range(nx-1):
                curr = offset_index + i + (nx*j)
                next_ = curr + 1
                next_line_curr = curr + nx
                next_line_next = next_line_curr + 1
                elems.append((curr, next_line_curr, next_line_next))
                elems.append((curr, next_, next_line_next))

        coord = list()
        for j in range(ny):
            for i in range(nx):
                coord.append((i + offset_x, j + offset_y))

        return elems, coord

    def distort_grid(self, elements, N, air_top, air_right, air_bottom, air_left):
        """
        Triangles of type 1 and 2 have weird, "distorted" hypotenuses:
            if "normal" ones positioned up-down, theirs position down-up.

        In conjunction with 'generate_grid' method you can generate grid
            for those triangles
        """
        nodes_in_row = air_left + N + air_right
        nodes_offset_top = nodes_in_row * air_top
        nodes_air_offset = air_left

        N -= 1
        elems_in_row = (air_left + N + air_right)*2
        offset_airTop = elems_in_row * air_top
        offset_airLeft = air_left*2

        for j in range(0, N):
            offset = offset_airTop + elems_in_row*j + offset_airLeft
            index = offset + (N-1-j)*2

            node = nodes_offset_top + nodes_in_row*j + nodes_air_offset + N-j-1
            node1 = node + 1
            node2 = nodes_offset_top + nodes_in_row*(j+1) + nodes_air_offset + N-j-1
            node3 = node2 + 1

            elements[index] = (node, node1, node2)
            elements[index+1] = (node1, node2, node3)


class Test_AbstractTest(AbstractTest):
    def test_gridDistorting_2x2_allAir1(self):
        air = 1
        N = 2
        elems, _ignore_ = self.generate_grid(N + air*2, N + air*2)
        self.distort_grid(elems, N, air, air, air, air)
        self.assertEqual(elems[8], "5 6 9\n", "Distortion went wrong")
        self.assertEqual(elems[9], "6 9 10\n", "Distortion went wrong")

    def test_gridDistorting_3x3_allAir1(self):
        air = 1
        N = 3
        elems, _ignore_ = self.generate_grid(N + air*2, N + air*2)
        self.distort_grid(elems, N, air, air, air, air)
        self.assertEqual(elems[12], "7 8 12\n", "Distortion went wrong")
        self.assertEqual(elems[13], "8 12 13\n", "Distortion went wrong")
        self.assertEqual(elems[18], "11 12 16\n", "Distortion went wrong")
        self.assertEqual(elems[19], "12 16 17\n", "Distortion went wrong")

    def test_gridDistorting_3x3_allAir2(self):
        air = 2
        N = 3
        elems, _ignore_ = self.generate_grid(N + air*2, N + air*2)
        self.distort_grid(elems, N, air, air, air, air)
        self.assertEqual(elems[30], "17 18 24\n", "Distortion went wrong")
        self.assertEqual(elems[31], "18 24 25\n", "Distortion went wrong")
        self.assertEqual(elems[40], "23 24 30\n", "Distortion went wrong")
        self.assertEqual(elems[41], "24 30 31\n", "Distortion went wrong")

    def test_triangleMaterialGeneration_2x2_type0_bareLeft_air2(self):
        material = self.generate_material(2, 0, 2, 2, 2, 0)
        ideal_result = [0]*12 + [1] + [0]*17
        self.assertEqual(material, ideal_result, "Material was generated with error")

    def test_TestGeneration(self):
        self.generate_testCase_triangle(2, 0, 1, 1, 1, 0, air=2)
