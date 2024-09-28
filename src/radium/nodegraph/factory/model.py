import qtawesome as qta
import typing

from PySide6 import QtGui, QtCore, QtWidgets

from radium.nodegraph import constants
from radium.nodegraph.factory.prototypes import NodeType


def iter_categories(node_type_name: str):
    """
    iterate over a category string e.g. General/Image and split it into (sub-namespace, name) pairs

    e.g.

    (General, General)
    (General/Image, Image)

    This makes it easy to populate the models Category items.
    """
    node_type_name = node_type_name.lstrip("/")
    last = 0

    for cursor, character in enumerate(node_type_name):
        if character == "/":
            result = node_type_name[:cursor], node_type_name[last:cursor]
            yield result
            last = cursor + 1

    yield node_type_name, node_type_name[last:]


class CategoryItem(QtGui.QStandardItem):
    def __init__(self, name):
        super().__init__(name)
        self.setEditable(False)
        self.setSelectable(False)
        self.setDragEnabled(False)
        self.setIcon(qta.icon("fa.folder"))


class NodePrototypeItem(QtGui.QStandardItem):
    def __init__(self, node_type: NodeType):
        super().__init__(node_type.name)
        self.node_prototype = node_type
        self.setEditable(False)
        self.setIcon(qta.icon("mdi6.box-shadow"))
        if isinstance(node_type.color, tuple):
            self.setData(
                QtGui.QColor(*node_type.color),
                role=QtCore.Qt.ItemDataRole.BackgroundRole,
            )


class NodePrototypeModel(QtGui.QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__category_items = {}
        self.__item_lookup = {}

    def removePrototype(self, name):
        item = self.__item_lookup.pop(name, None)
        if item:
            index = self.indexFromItem(item)
            self.removeRow(index.row(), parent=index.parent())

    def addPrototype(self, prototype: NodeType):
        parent = self.invisibleRootItem()

        for category, name in iter_categories(prototype.category):
            if category not in self.__category_items:
                new_parent = self.__category_items[category] = CategoryItem(name)
                parent.appendRow(new_parent)
                parent = new_parent
            else:
                parent = self.__category_items[category]

        item = NodePrototypeItem(prototype)

        self.__category_items[prototype.type_name] = item
        parent.appendRow(item)

    def mimeTypes(self):
        return [constants.NODE_TYPE_MIME_TYPE]

    def mimeData(self, indexes: typing.List[QtCore.QModelIndex]):
        item = self.itemFromIndex(indexes[0])
        mimeData = QtCore.QMimeData()

        if isinstance(item, NodePrototypeItem):
            mimeData.setText(item.node_prototype.type_name)
            mimeData.setData(
                constants.NODE_TYPE_MIME_TYPE, item.node_prototype.type_name.encode()
            )

        return mimeData


if __name__ == "__main__":
    app = QtWidgets.QApplication()
    prototype = NodeType(
        name="Merge",
        category="General/Image",
    )

    model = NodePrototypeModel()
    model.addPrototype(prototype)

    view = QtWidgets.QTreeView()
    view.setModel(model)
    view.setDragEnabled(True)
    view.setIconSize(QtCore.QSize(32, 32))
    view.show()
    app.exec()
