import typing

from PySide6 import QtCore, QtGui, QtWidgets
from radium.nodegraph.browser.model import NodePrototypeModel


class SomeItemView(typing.Protocol):
    def setModel(self, model: QtCore.QAbstractItemModel) -> None:
        pass


class NodeBrowserController(QtCore.QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = NodePrototypeModel()

    def addPrototype(self, prototype):
        self.model.addPrototype(prototype)

    def clearPrototypes(self):
        self.model.clear()

    def attachView(self, view: SomeItemView):
        view.setModel(self.model)
