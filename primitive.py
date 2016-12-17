from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
from rectangle import NewRectangleWidget
from triangle import NewTriangleWidget


class NewPrimitiveDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        uic.loadUi('ui/new_primitive.ui', self)

        self.tabWidget.clear()  # Очистим пустые страницы
        self.Rectangle_widget = NewRectangleWidget()
        self.Triangle_widget = NewTriangleWidget()
        self.tabWidget.addTab(self.Rectangle_widget, "Прямоугольник")
        self.tabWidget.addTab(self.Triangle_widget, "Треугольник")

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

    def for_expanding(self, prim, side_code):
        curr_tab_index = self.tabWidget.currentIndex()
        if curr_tab_index == 0:
            self.Rectangle_widget.for_expanding(prim, side_code)
        elif curr_tab_index == 1:
            return self.Triangle_widget.get_data(prim, side_code)
