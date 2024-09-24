import typing
from PySide6 import QtCore, QtGui

from radium.nodegraph.graph.scene.node import Node
from radium.nodegraph.graph.scene.event_filter import SceneEventFilter
from radium.nodegraph.graph.scene.backdrop import Backdrop
from radium.nodegraph.graph.scene import NodeGraphScene, commands
from radium.nodegraph.graph.scene.port import InputPort, OutputPort
from radium.nodegraph.graph.scene.connection import Connection
from radium.nodegraph.graph.scene.prototypes import NodePrototype

if typing.TYPE_CHECKING:
    from radium.nodegraph.graph.view import NodeGraphView


class NodeGraphController(QtCore.QObject):
    prototypeRegistered = QtCore.Signal(NodePrototype)

    def __init__(self, undo_stack: QtGui.QUndoStack = None, parent=None):
        super().__init__(parent)
        self.scene = NodeGraphScene()
        self.undo_stack = undo_stack or QtGui.QUndoStack()
        self.scene_event_filter = SceneEventFilter(self.scene, self.undo_stack)
        self.__prototypes = {}

    def attachView(self, view: "NodeGraphView"):
        view.setScene(self.scene)
        view.createNodeRequested.connect(self.onNodeCreationRequested)

    def registerPrototype(self, prototype: NodePrototype):
        self.__prototypes[prototype.node_type] = prototype
        self.prototypeRegistered.emit(prototype)

    def createNode(self, node_type) -> Node:
        prototype = self.__prototypes[node_type]
        cmd = commands.CreateNodeCommand(self.scene, prototype)
        cmd.setText(f"Create: {prototype.node_type}")
        self.undo_stack.push(cmd)
        return cmd.node

    def createBackdrop(self, name):
        backdrop = Backdrop(name)
        cmd = commands.AddItemCommand(self.scene, backdrop)
        cmd.setText("Create Backdrop")
        self.undo_stack.push(cmd)

    def removeItem(self, item):
        cmd = commands.RemoveItemCommand(self.scene, item)
        cmd.setText(f"Remove: {item}")
        self.undo_stack.push(cmd)

    def selectedNodes(self):
        return [n for n in self.scene.selectedItems() if isinstance(n, Node)]

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

    @QtCore.Slot(str, QtCore.QPointF)
    def onNodeCreationRequested(self, node_type: str, position: QtCore.QPointF):
        node = self.createNode(node_type)
        node.setPos(position)
