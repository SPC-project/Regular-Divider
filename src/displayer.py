from PyQt5.QtGui import QColor, QPolygon, QBrush
from PyQt5.QtCore import QPoint, Qt
from Sorter import read_pmd

PADDING = 10  # Space between window border and QFrame
OFFSET = 4  # QFrame's area start not at (0;0), but (4;4) because curving
CAMERA_OFFSET = 3
BLANK = QColor(0, 0, 0, 0)
COL_AIR = QColor(128, 176, 241, 127)
COL_AIR_INNER = QColor(128, 176, 241, 24)
COL_FIG = QColor(46, 61, 73)
COL_FIG_INNNER = QColor(46, 61, 73, 64)
COL_TEXT = QColor(0, 0, 0)


class PMD_Displayer():
    def __init__(self):
        self.data = False
        self.buffer = False
        self.show_indexes = True

    def load_pmd(self, filename):
        self.filename = filename
        In = open(filename, 'r')
        elems, coords, mat = read_pmd(In)

        # Prepare data
        def describe_element(index, elem):
            A, B, C = elem
            first = (coords[A][0], coords[A][1])
            second = (coords[B][0], coords[B][1])
            third = (coords[C][0], coords[C][1])
            return (first, second, third, mat[index])

        self.data = tuple(
            describe_element(i, elem) for i, elem in enumerate(elems)
        )

        # Figure out the camera's parameters
        coords.sort(key=lambda node: (node[1], node[0]))
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
        self.longest_index = max([str(min_x), str(min_y), str(max_x), str(max_y)])

        self.coords = coords

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

        if not self.show_indexes:
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

        for index, node in enumerate(self.coords):
            if index % skip == 0:
                x, y = scale(node)
                canvas.drawText(x + 2, y - 2, str(index))

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
