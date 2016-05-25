from PyQt5.QtWidgets import QWidget, QDialog, QListWidgetItem
from PyQt5 import uic


class PrimitivesListDialog(QDialog):
    def __init__(self):
        super(PrimitivesListDialog, self).__init__()
        uic.loadUi('ui/edit_figure.ui', self)

    def show(self, figure):
        self.figure = figure
        self.primitives.clear()

        for pr in figure.shape:
            li = ListItem(self.primitives, pr)
            li.name.clicked.connect(self.editEvent)
            li.remove.clicked.connect(self.removeEvent)

        self.exec_()

    def removeEvent(self):
        pr = self.primitives
        self.figure.primitive_deletion.emit(pr.currentRow())
        pr.removeItemWidget(pr.currentItem())

    def editEvent(self):
        pr = self.primitives
        self.figure.primitive_modification.emit(pr.currentRow())
        self.close()

    def resizeEvent(self, event):
        x = event.size().width()
        y = event.size().height()
        self.primitives.resize(x, y - self.label.height())


class ListItem(QWidget):
    def __init__(self, parent, primitive):
        super(ListItem, self).__init__(parent)
        uic.loadUi('ui/list_item.ui', self)

        x = primitive.x
        y = primitive.y
        w = primitive.width
        h = primitive.height
        self.name.setText("({:g};{:g}) {:g}x{:g}".format(x, y, w, h))

        self.item = QListWidgetItem(parent)
        self.item.setSizeHint(self.size())
        parent.setItemWidget(self.item, self)
