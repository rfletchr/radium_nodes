import typing
import uuid

from PySide6 import QtGui, QtWidgets, QtCore
from radium.nodegraph.graph.scene import NodeGraphScene
from radium.nodegraph.graph.scene.node import Node
from radium.nodegraph.graph.scene.connection import Connection
from radium.nodegraph.graph.scene.port import InputPort, OutputPort

if typing.TYPE_CHECKING:
    from radium.nodegraph.graph.scene.prototypes import NodePrototype

MOVE_NODES_COMMAND_ID = 1000


class CreateNodeCommand(QtGui.QUndoCommand):
    def __init__(self, scene: NodeGraphScene, prototype: "NodePrototype"):
        super().__init__()
        self.setText("Create Node")
        self.scene = scene
        self.prototype = prototype
        self.node: typing.Optional[Node] = None

    def redo(self):
        if self.node is None:
            self.node = Node.fromPrototype(self.prototype)

        self.scene.addItem(self.node)

    def undo(self):
        self.scene.removeItem(self.node)


class CreateConnectionCommand(QtGui.QUndoCommand):
    def __init__(
        self,
        scene: "NodeGraphScene",
        output_port: OutputPort,
        input_port: InputPort,
    ):
        super().__init__()
        self.setText("Create Connection")
        self.scene = scene
        self.connection = Connection(output_port, input_port)
        self.sub_commands = []

        input_connections = input_port.connections()

        if len(input_connections) + 1 > input_port.maxConnections():
            self.sub_commands.append(RemoveItemCommand(scene, input_connections[-1]))

        output_connections = output_port.connections()

        if len(output_connections) + 1 > output_port.maxConnections():
            self.sub_commands.append(RemoveItemCommand(scene, output_connections[-1]))

    def redo(self):
        self.scene.addItem(self.connection)
        for cmd in self.sub_commands:
            cmd.redo()

    def undo(self):
        self.scene.removeItem(self.connection)
        for cmd in self.sub_commands:
            cmd.undo()


class AddItemCommand(QtGui.QUndoCommand):
    def __init__(
        self,
        scene: "NodeGraphScene",
        item: QtWidgets.QGraphicsItem,
        parent=None,
    ):
        super().__init__(parent)
        self.scene = scene
        self.item = item

    def redo(self):
        self.scene.addItem(self.item)

    def undo(self):
        self.scene.removeItem(self.item)


class RemoveItemCommand(QtGui.QUndoCommand):
    def __init__(
        self,
        scene: "NodeGraphScene",
        item: QtWidgets.QGraphicsItem,
        parent=None,
    ):
        super().__init__(parent)
        self.scene = scene
        self.item = item

    def redo(self):
        self.scene.removeItem(self.item)

    def undo(self):
        self.scene.addItem(self.item)


class MoveNodesCommand(QtGui.QUndoCommand):
    def __init__(
        self,
        nodes: typing.Union[typing.List[Node], typing.Set[Node]],
        offset: QtCore.QPointF,
        drag_id: str = None,
        parent=None,
    ):
        super().__init__(parent=parent)
        self.setText(f"Move ({len(nodes)}) Nodes")
        self.nodes = nodes
        self.drag_id = drag_id or uuid.uuid4().hex
        self.offset = offset

    def mergeWith(self, other):
        if isinstance(other, MoveNodesCommand) and other.drag_id == self.drag_id:
            self.offset += other.offset
            return True
        return False

    def id(self):
        return MOVE_NODES_COMMAND_ID

    def redo(self):
        for node in self.nodes:
            node.moveBy(self.offset.x(), self.offset.y())

    def undo(self):
        for node in self.nodes:
            node.moveBy(-self.offset.x(), -self.offset.y())


class CloneNodeCommand(QtGui.QUndoCommand):
    def __init__(
        self, scene: "NodeGraphScene", node: "Node", position=None, parent=None
    ):
        super().__init__(parent=parent)
        self.setText("Clone Node")
        self.scene = scene
        self.node = Node.fromNode(node)
        self.node.setPos(position if position is not None else node.pos())

    def redo(self):
        self.scene.addItem(self.node)

    def undo(self):
        self.scene.removeItem(self.node)
