from PyQt5.QtGui import QColor, QPolygon, QBrush
from PyQt5.QtCore import QPoint, Qt
from src.output import SECTIONS_NAMES

PADDING = 10  # Space between window border and QFrame
OFFSET = 4  # QFrame's area start not at (0;0), but (4;4) because curving
CAMERA_OFFSET = 3
BLANK = QColor(0, 0, 0, 0)
NODE_LABEL_OFFSET_X = 2
NODE_LABEL_OFFSET_Y = -2
COL_AIR = QColor(128, 176, 241, 127)
COL_AIR_INNER = QColor(128, 176, 241, 24)
COL_FIG = QColor(46, 61, 73)
COL_FIG_INNNER = QColor(46, 61, 73, 64)
COL_TEXT = QColor(0, 0, 0)

TEMP_DIR = ".temp/"


def read_pmd(In):
    is_header = True
    is_elements = False
    is_nodes = False
    is_stuff = False

    elements = list()
    coordinates = list()
    material = list()
    index = 0

    for line in In.readlines():
        if is_header:
            if line == SECTIONS_NAMES[1]:
                is_header = False
                is_elements = True
        elif is_elements:
            if line != SECTIONS_NAMES[2]:
                elem = line.split(' ')
                elements.append((int(elem[0]), int(elem[1]), int(elem[2])))
            else:
                is_elements = False
                is_nodes = True
        elif is_nodes:
            if line != SECTIONS_NAMES[3]:
                x, y = [float(coor) for coor in line.split(' ')]
                coordinates.append((x, y))
                index += 1
            else:
                is_nodes = False
                is_stuff = True
        elif is_stuff:
            if line == SECTIONS_NAMES[5]:  # skip force and contacts
                is_stuff = False
        else:
            material.append(int(line.strip()))

    return elements, coordinates, material


class PMD_Displayer():
    def __init__(self, send_message):
        self.data = False
        self.buffer = False
        self.index_option = 1
        self.send_message = send_message

    def load_pmd(self, filename):
        self.filename = filename
        In = open(filename, 'r')
        elems, coords, mat = read_pmd(In)

        # Prepare data
        def describe_element(index, elem):
            A, B, C = elem
            first = coords[A]
            second = coords[B]
            third = coords[C]
            return (first, second, third, mat[index])

        self.data = tuple(
            describe_element(i, elem) for i, elem in enumerate(elems)
        )

        # Figure out the camera's parameters
        max_x = max(coords, key=lambda node: node[0])[0]
        max_y = max(coords, key=lambda node: node[1])[1]
        min_x = min(coords, key=lambda node: node[0])[0]
        min_y = min(coords, key=lambda node: node[1])[1]
        dx = max_x - min_x + 2*CAMERA_OFFSET
        dy = max_y - min_y + 2*CAMERA_OFFSET
        self.world_size = max(dx, dy)
        self.start_x = min_x - CAMERA_OFFSET
        self.start_y = min_y - CAMERA_OFFSET
        self.between_nodes = coords[1][0] - coords[0][0]
        if abs(self.between_nodes) < 0.00000001:
            self.between_nodes = coords[1][1] - coords[0][1]
        self.longest_index = max([str(min_x), str(min_y), str(max_x), str(max_y)])

        self.coords = coords
        In.close()

    def display_pmd(self, canvas, camera_x, camera_y, kx, ky):
        if not self.data:
            return

        def scale(vertex):
            canvas_x = int(round((camera_x + vertex[0])*kx))
            canvas_y = int(round((camera_y + vertex[1])*ky))
            return (canvas_x, canvas_y)

        for A, B, C, material in self.data:
            self.draw_element(canvas, A, B, C, material, scale)

        canvas.setPen(COL_TEXT)
        canvas.drawText(0, 10, self.filename + ":")

        if self.index_option == 0:
            return

        metrics = canvas.fontMetrics()
        MFlag = Qt.TextSingleLine
        label_metric = metrics.size(MFlag, self.longest_index)
        skip = 1
        label_w = label_metric.width() + 2
        label_h = label_metric.height() + 2
        free_space = self.between_nodes*kx
        if label_w > free_space and label_h > free_space and int(label_w / free_space) < 3:
            skip = 2
        elif int(label_w / free_space) > 3:
            return

        if self.index_option == 1:  # Display all indexes
            self.display_all_nodes(skip, scale, canvas)
        elif self.index_option == 2:
            self.display_border_nodes(skip, scale, canvas)

    def display_all_nodes(self, skip, scale, canvas):
        for index, node in enumerate(self.coords):
            if index % skip == 0:
                x, y = scale(node)
                canvas.drawText(x + NODE_LABEL_OFFSET_X, y + NODE_LABEL_OFFSET_Y, str(index))

    def display_border_nodes(self, skip, scale, canvas):
        border_filename = self.filename + ".outer_nodes"
        Out = open(border_filename, 'w')

        nodes = dict()

        for A, B, C, material in self.data:
            for dot in [A, B, C]:
                if dot not in nodes:
                    nodes[dot] = {'fig': material == 1, 'air': material == 0}
                else:
                    nodes[dot]['fig'] = nodes[dot]['fig'] or material == 1
                    nodes[dot]['air'] = nodes[dot]['air'] or material == 0

        for index, (x, y) in enumerate(self.coords):
            node = nodes[(x, y)]
            if node["fig"] and node["air"]:
                x, y = scale([x, y])
                canvas.drawText(x + NODE_LABEL_OFFSET_X, y + NODE_LABEL_OFFSET_Y, str(index))
                Out.write(str(index) + "\n")

        Out.close()
        self.send_message("Граничные узлы сохранены в файл: " + border_filename)

    def draw_element(self, canvas, A, B, C, material, scale):
        first = QPoint(*scale(A))
        second = QPoint(*scale(B))
        third = QPoint(*scale(C))

        element = QPolygon()
        element.append(first)
        element.append(second)
        element.append(third)
        element.append(first)
        if material == 1:
            canvas.setPen(COL_FIG)
            canvas.setBrush(QBrush(COL_FIG_INNNER))  # drawPolygon() use it
        else:
            canvas.setPen(COL_AIR)
            canvas.setBrush(QBrush(COL_AIR_INNER))
        canvas.drawPolygon(element)
