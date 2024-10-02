import typing
from PySide6 import QtCore, QtGui, QtWidgets

from radium.nodegraph.graph.scene.node import Node
from radium.nodegraph.graph.scene.event_filter import SceneEventFilter
from radium.nodegraph.graph.scene.backdrop import Backdrop
from radium.nodegraph.graph.scene import NodeGraphScene, commands
from radium.nodegraph.graph.scene.port import InputPort, OutputPort
from radium.nodegraph.graph.scene.connection import Connection
from radium.nodegraph.factory.factory import NodeFactory

if typing.TYPE_CHECKING:
    from radium.nodegraph.graph.view import NodeGraphView


class NodeGraphController(QtCore.QObject):
    def __init__(
        self,
        undo_stack: QtGui.QUndoStack = None,
        node_factory: NodeFactory = None,
        parent=None,
    ):
        super().__init__(parent)
        self.scene = NodeGraphScene()
        self.node_factory = node_factory or NodeFactory()
        self.undo_stack = undo_stack or QtGui.QUndoStack()

        self.scene_event_filter = SceneEventFilter(
            self.scene,
            self.undo_stack,
            self.node_factory,
        )

    def attachView(self, view: "NodeGraphView"):
        view.setScene(self.scene)
        view.createNodeRequested.connect(self.onNodeCreationRequested)
        self.setupActions(view)

    def setupActions(self, view: "NodeGraphView"):
        view_action = QtGui.QAction("Edit Node", self)
        view_action.setData(view)
        view_action.setShortcut("V")
        view_action.triggered.connect(self.onViewActionTriggered)
        view.addAction(view_action)

        action = QtGui.QAction("Edit Node", self)
        action.setData(view)
        action.setShortcut("E")
        action.triggered.connect(self.onEditActionTriggered)
        view.addAction(action)

        action = QtGui.QAction("Edit Node+", self)
        action.setData(view)
        action.setShortcut("Shift+E")
        action.triggered.connect(self.onEditActionTriggered)
        view.addAction(action)

    def createNode(self, node_type) -> Node:
        node_type = self.node_factory.getNodeType(node_type)
        cmd = commands.CreateNodeCommand(self.scene, node_type, self.node_factory)
        cmd.setText(f"Create: {node_type.type_name}")

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

    @QtCore.Slot()
    def onViewActionTriggered(self):
        action = self.sender()
        view: "NodeGraphView" = action.data()
        cursor = QtGui.QCursor.pos()
        view_cursor = view.mapFromGlobal(cursor)
        scene_pos = view.mapToScene(view_cursor)

        hovered_item = self.scene.itemAt(scene_pos, QtGui.QTransform())

        if isinstance(hovered_item, Node):
            hovered_item.setViewed(not hovered_item.isViewed())

            for node in self.scene.nodes():
                if node is hovered_item:
                    continue
                node.setViewed(False)

    @QtCore.Slot()
    def onEditActionTriggered(self):
        action = self.sender()
        view: "NodeGraphView" = action.data()
        cursor = QtGui.QCursor.pos()
        view_cursor = view.mapFromGlobal(cursor)
        scene_pos = view.mapToScene(view_cursor)

        modifiers = QtWidgets.QApplication.keyboardModifiers()
        hovered_item = self.scene.itemAt(scene_pos, QtGui.QTransform())

        if isinstance(hovered_item, Node):
            hovered_item.setEdited(not hovered_item.isEdited())

        if modifiers & QtCore.Qt.KeyboardModifier.ShiftModifier:
            return

        for node in self.scene.nodes():
            if node is hovered_item:
                continue
            node.setEdited(False)
