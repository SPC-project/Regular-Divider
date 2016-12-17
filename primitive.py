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

    def grab_focus(self):
        self.tabWidget.currentWidget().x.setFocus()

    def get_data(self):
        curr_tab_index = self.tabWidget.currentIndex()
        if curr_tab_index == 0:
            return self.Rectangle_widget.get_data()
        elif curr_tab_index == 1:
            return self.Triangle_widget.get_data()
