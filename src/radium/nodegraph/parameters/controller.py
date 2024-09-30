import typing

from PySide6 import QtCore, QtGui, QtWidgets

from radium.nodegraph.parameters.parameter import Parameter

if typing.TYPE_CHECKING:
    from radium.nodegraph.parameters.view.view import ParameterEditorView
    from radium.nodegraph.graph.scene.node import Node


class ParameterEditorController(QtCore.QObject):
    def __init__(self, undo_stack: QtGui.QUndoStack, parent=None):
        super().__init__(parent=parent)
        self.view: typing.Optional["ParameterEditorView"] = None
        self.undo_stack = undo_stack

    def onEditorValueChanged(self, parameter: Parameter, value: typing.Any):
        cmd = ChangeParameterCommand(parameter, value)
        self.undo_stack.push(cmd)

    def attachView(self, view: "ParameterEditorView"):
        self.view = view
        self.view.editorValueChanged.connect(self.onEditorValueChanged)

    def setNode(self, node: "Node"):
        if self.view is None:
            return
        self.view.clear()
        self.view.addParameters(node.parameters().values())

    def clear(self):
        self.view.clear()


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
