from PyQt5.QtWidgets import QWidget, QDialog, QListWidgetItem
from PyQt5 import uic


class PrimitivesListDialog(QDialog):
    def __init__(self):
        super(PrimitivesListDialog, self).__init__()
        uic.loadUi('ui/edit_figure.ui', self)

    def show(self, figure):
        self.primitives.clear()

        id = 0
        for pr in figure.shape:
            ListItem(self.primitives, pr, id, figure.primitive_deletion,
                     figure.primitive_modification)
            id += 1

        self.exec_()

    def resizeEvent(self, event):
        x = event.size().width()
        y = event.size().height()
        self.primitives.resize(x, y - self.label.height())


class ListItem(QWidget):
    def __init__(self, parent, primitive, id, sig_del, sig_mod):
        super(ListItem, self).__init__(parent)
        uic.loadUi('ui/list_item.ui', self)

        self.id = id
        self.sig_del = sig_del
        self.sig_mod = sig_mod
        self.parent = parent
        x = primitive.x
        y = primitive.y
        w = primitive.width
        h = primitive.height
        self.name.setText("({:g};{:g}) {:g}x{:g}".format(x, y, w, h))

        self.name.clicked.connect(self.modify)
        self.remove.clicked.connect(self.delete)

        self.item = QListWidgetItem(parent)
        self.item.setSizeHint(self.size())
        parent.setItemWidget(self.item, self)

    def modify(self):
        self.sig_mod.emit(self.id)

    def delete(self):
        self.parent.removeItemWidget(self.item)
        self.sig_del.emit(self.id)
