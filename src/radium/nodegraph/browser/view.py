import sys

from PySide6 import QtWidgets, QtGui, QtCore


class NodeBrowserView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tree_view = QtWidgets.QTreeView()
        self.tree_view.setDragEnabled(True)
        self.tree_view.setSelectionMode(self.tree_view.SelectionMode.SingleSelection)
        self.tree_view.setHeaderHidden(True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.tree_view)

    def setModel(self, model):
        self.tree_view.setModel(model)


if __name__ == "__main__":
    app = QtWidgets.QApplication()
    model = QtGui.QStandardItemModel()
    item = QtGui.QStandardItem("Node")
    model.appendRow(item)

    view = NodeBrowserView()
    view.setModel(model)

    view.show()

    app.exec()
