import typing

from PySide6 import QtCore, QtGui, QtWidgets

if typing.TYPE_CHECKING:
    from radium.nodegraph.parameters.view.view import ParameterEditorView
    from radium.nodegraph.graph.scene.node import Node


class ParameterEditorController(QtCore.QObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.view: typing.Optional["ParameterEditorView"] = None

    def attachView(self, view: "ParameterEditorView"):
        self.view = view

    def setNode(self, node: "Node"):
        if self.view is None:
            return
        self.view.clear()
        self.view.addParameters(node.parameters().values())

    def clear(self):
        self.view.clear()
