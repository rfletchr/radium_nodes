from PySide6 import QtCore, QtWidgets, QtGui
import rapidfuzz


class NodeSearchBox(QtWidgets.QWidget):
    itemSelected = QtCore.Signal(QtCore.QModelIndex)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.proxy_model = FuzzySortProxyModel()

        self.search = QtWidgets.QLineEdit()
        self.search.returnPressed.connect(self.onEnterPressed)

        self.list_view = QtWidgets.QListView()
        self.list_view.setModel(self.proxy_model)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.search)
        layout.addWidget(self.list_view)

        self.search.textChanged.connect(self.onTextChanged)
        self.list_view.doubleClicked.connect(self.onItemClicked)
        self.list_view.clicked.connect(self.onItemClicked)

    def onTextChanged(self, text):
        self.proxy_model.setQuery(text)
        self.list_view.setCurrentIndex(self.proxy_model.index(0, 0))

    def onItemClicked(self, index: QtCore.QModelIndex):
        self.close()
        self.itemSelected.emit(self.proxy_model.mapToSource(index))

    def setModel(self, model):
        self.proxy_model.setSourceModel(model)

    def onEnterPressed(self):
        proxy_index = self.list_view.currentIndex()
        model_index = self.proxy_model.mapToSource(proxy_index)
        self.close()
        self.itemSelected.emit(model_index)

    def show(self):
        super().show()
        self.search.setFocus()


class FuzzySortProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self, query="", parent=None):
        super().__init__(parent)
        self.query = query

    def setQuery(self, query):
        self.query = query
        self.invalidate()
        self.sort(0, order=QtCore.Qt.SortOrder.DescendingOrder)

    def lessThan(self, left, right):
        left_data = self.sourceModel().data(left, QtCore.Qt.ItemDataRole.DisplayRole)
        right_data = self.sourceModel().data(right, QtCore.Qt.ItemDataRole.DisplayRole)

        if left_data and right_data:
            left_score = rapidfuzz.fuzz.ratio(self.query, left_data)
            right_score = rapidfuzz.fuzz.ratio(self.query, right_data)

            return left_score < right_score
        return False


if __name__ == "__main__":
    app = QtWidgets.QApplication()
    # model = QtGui.QStandardItemModel()
    #
    # for name in ["Merge", "MergeImage", "MergeFloat", "Constant", "Blur"]:
    #     item = QtGui.QStandardItem(name)
    #     item.setEditable(False)
    #     model.appendRow(item)
    #
    # view = NodeSearchBox()
    # view.itemSelected.connect(
    #     lambda index: print(index.data(QtCore.Qt.ItemDataRole.DisplayRole))
    # )
    # view.setModel(model)
    #
    # view.show()
    menu = QtWidgets.QMenu()

    menu.addAction("Bork")
    menu.show()

    app.exec()
