from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5 import uic

from primitive_dialogues import NewRectangleWidget
from primitive_dialogues import NewTriangleWidget

import abc


class NewPrimitiveDialog(QDialog):
    def __init__(self):
        super(NewPrimitiveDialog, self).__init__()
        uic.loadUi('ui/new_primitive.ui', self)

        self.tabWidget.clear()  # Очистим пустые страницы
        self.Rectangle_widget = NewRectangleWidget()
        self.Triangle_widget = NewTriangleWidget()
        self.tabWidget.addTab(self.Rectangle_widget, "Прямоугольник")
        self.tabWidget.addTab(self.Triangle_widget, "Треугольник")

        self.accepted.connect(self.validate)

        self.tabWidget.currentChanged.connect(self.grab_focus)

    def grab_focus(self):
        self.tabWidget.currentWidget().x.setFocus()

    def get_data(self):
        curr_tab_index = self.tabWidget.currentIndex()
        fig = None
        mesh = None
        if curr_tab_index == 0:
            fig, mesh = self.Rectangle_widget.get_data()
        elif curr_tab_index == 1:
            fig, mesh = self.Triangle_widget.get_data()

        return fig, mesh, curr_tab_index

    def validate(self):
        curr = self.tabWidget.currentWidget()
        if curr.height.value() == 0 or curr.width.value() == 0:
            msg = QMessageBox(QMessageBox.Critical, "Неверное значение!",
                              'Ширина и высота не могут быть равны 0')
            msg.exec_()
            self.done(0)

    def for_expanding(self, prim, side_code):
        curr_tab_index = self.tabWidget.currentIndex()
        if curr_tab_index == 0:
            self.Rectangle_widget.for_expanding(prim, side_code)
        elif curr_tab_index == 1:
            return self.Triangle_widget.get_data(prim, side_code)


class AbstractPrimitive:
    __metaclass__ = abc.ABCMeta

    def __init__(self, fig, mesh):
        self.x, self.y, self.width, self.height = fig
        self.mesh = mesh

        self.element_count_w = mesh.NAL + mesh.NFX + mesh.NAR
        self.element_count_h = mesh.NAT + mesh.NFY + mesh.NAB
        self.step_x = self.width/mesh.NFX
        self.step_y = self.height/mesh.NFY
        self.start_x = self.x - self.step_x*mesh.NAL  # where air start
        self.start_y = self.y - self.step_y*mesh.NAT
        width = self.mesh.NFX + self.mesh.NAR
        height = self.mesh.NFY + self.mesh.NAB
        self.end_x = self.x + self.step_x*width
        self.end_y = self.y + self.step_y*(height)

        self.modify()

    @abc.abstractmethod
    def modify(self):
        pass

    def get_box(self):
        return (self.start_x, self.start_y, self.end_x, self.end_y)

    def draw(self, canvas, mesh_canvas, shift_x, shift_y, kx, ky):
        def pixel_x(n_elements):
            val = shift_x + self.start_x + n_elements*self.step_x
            return int(round(val*kx))

        def pixel_y(n_elements):
            val = shift_y + self.start_y + n_elements*self.step_y
            return int(round(val*ky))

        self.draw_figure(canvas, shift_x, shift_y, kx, ky)
        self.draw_mesh(mesh_canvas, pixel_x, pixel_y)

    @abc.abstractmethod
    def draw_figure(self, canvas, shift_x, shift_y, kx, ky):
        pass

    @abc.abstractmethod
    def draw_mesh(self, canvas, pixel_x, pixel_y):
        pass
