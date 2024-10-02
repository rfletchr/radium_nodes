import typing

from PySide6 import QtCore, QtGui, QtWidgets

from radium.nodegraph.parameters.parameter import Parameter
from radium.nodegraph.parameters.view import editors

if typing.TYPE_CHECKING:
    from radium.nodegraph.parameters.view.view import ParameterEditorView
    from radium.nodegraph.graph.scene.node import Node


class ParameterEditorController(QtCore.QObject):
    def __init__(self, undo_stack: QtGui.QUndoStack, parent=None):
        super().__init__(parent=parent)
        self.view: typing.Optional["ParameterEditorView"] = None
        self.undo_stack = undo_stack
        self.__node_id_to_widget = {}

    def onEditorValueChanged(self, parameter: Parameter, value: typing.Any):
        cmd = ChangeParameterCommand(parameter, value)
        self.undo_stack.push(cmd)

    def attachView(self, view: "ParameterEditorView"):
        self.view = view
        self.view.editorValueChanged.connect(self.onEditorValueChanged)

    def addNode(self, node: "Node"):
        if not self.view:
            return

        self.view.addNode(node)

    def removeNode(self, node: "Node"):
        if not self.view:
            return

        self.view.removeNode(node)


class ChangeParameterCommand(QtGui.QUndoCommand):
    def __init__(self, parameter: Parameter, value: typing.Any, parent=None):
        super().__init__(parent)
        self.setText(f"set: {parameter.name()}")
        self.parameter = parameter
        self.old_value = parameter.value()
        self.value = value

    def redo(self):
        self.parameter.setValue(self.value)

    def undo(self):
        self.parameter.setValue(self.old_value)
