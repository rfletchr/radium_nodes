import typing
from PySide6 import QtCore, QtGui, QtWidgets

from radium.nodegraph.scene.node import Node
from radium.nodegraph.scene import SceneEventFilter
from radium.nodegraph.scene.backdrop import Backdrop
from radium.nodegraph.scene.scene import NodeGraphScene
from radium.nodegraph.scene.port import InputPort, OutputPort
from radium.nodegraph.scene.connection import Connection
from radium.nodegraph.scene.prototypes import NodePrototype
from radium.nodegraph.scene import commands

if typing.TYPE_CHECKING:
    from radium.nodegraph.view import NodeGraphView


class NodeGraphController(QtCore.QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = NodeGraphScene()
        self.undo_stack = QtGui.QUndoStack()
        self.scene_event_filter = SceneEventFilter(self.scene, self.undo_stack)
        self.__prototypes = {}
        self.nodes_model = QtGui.QStandardItemModel()

    def attachView(self, view: "NodeGraphView"):
        view.createNodeRequested.connect(self.onNodeCreationRequested)
        view.setNodesModel(self.nodes_model)
        view.setScene(self.scene)

    def onNodeCreationRequested(self, index: QtCore.QModelIndex, position: QtCore.QPointF):
        prototype = index.data(QtCore.Qt.ItemDataRole.UserRole)
        node = self.createNode(prototype.node_type)
        node.setPos(position)

    def registerPrototype(self, prototype: NodePrototype):
        self.__prototypes[prototype.node_type] = prototype
        item = QtGui.QStandardItem(prototype.node_type)
        item.setEditable(False)
        item.setData(prototype, QtCore.Qt.ItemDataRole.UserRole)
        self.nodes_model.appendRow(item)

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

