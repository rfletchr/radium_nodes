from PySide6 import QtCore, QtGui

from radium.nodegraph.scene.node import Node
from radium.nodegraph.scene import SceneEventFilter
from radium.nodegraph.scene.backdrop import Backdrop
from radium.nodegraph.scene.scene import NodeGraphScene
from radium.nodegraph.scene.port import InputPort, OutputPort
from radium.nodegraph.scene.connection import Connection
from radium.nodegraph.scene.prototypes import NodePrototype
from radium.nodegraph.scene import commands

INITIAL_SCENE_RECT = (-10000, -10000, 20000, 20000)


class NodeGraphController(QtCore.QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = NodeGraphScene()
        self.undo_stack = QtGui.QUndoStack()
        self.scene_event_filter = SceneEventFilter(self.scene, self.undo_stack)

    def createNode(self, prototype: NodePrototype) -> Node:
        cmd = commands.CreateNodeCommand(self.scene, prototype)
        cmd.setText(f"Create: {prototype.node_type}")
        self.undo_stack.push(cmd)
        return cmd.node

    def createBackdrop(self, name):
        backdrop = Backdrop(name)
        cmd = commands.AddItemCommand(self.scene, backdrop)
        cmd.setText("Create Backdrop")
        self.undo_stack.push(cmd)

    def createConnection(
        self, output_port: OutputPort, input_port: InputPort
    ) -> Connection:
        if not isinstance(output_port, OutputPort):
            raise TypeError(f"Not an output port: {output_port}")

        if not isinstance(input_port, InputPort):
            raise TypeError(f"Not an input port: {input_port}")

        cmd = commands.CreateConnectionCommand(self.scene, output_port, input_port)
        self.undo_stack.push(cmd)
        return cmd.connection
