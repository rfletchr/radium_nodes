import typing
import logging

from PySide6 import QtCore, QtGui, QtWidgets

from radium.nodegraph.graph.scene.group import Group
from radium.nodegraph.graph.scene.node import Node
from radium.nodegraph.graph.scene.event_filter import SceneEventFilter
from radium.nodegraph.graph.scene.backdrop import Backdrop
from radium.nodegraph.graph.scene import NodeGraphScene, commands
from radium.nodegraph.graph.scene.port import InputPort, OutputPort
from radium.nodegraph.graph.scene.connection import Connection
from radium.nodegraph.factory.factory import NodeFactory
from radium.nodegraph.parameters.parameter import Parameter


if typing.TYPE_CHECKING:
    from radium.nodegraph.graph.view import NodeGraphView


logger = logging.getLogger(__name__)


class NodeGraphController(QtCore.QObject):
    scenePushed = QtCore.Signal(NodeGraphScene)
    scenePopped = QtCore.Signal()

    nodeEdited = QtCore.Signal(Node)
    nodeSelected = QtCore.Signal(Node)
    parameterChanged = QtCore.Signal(Node, Parameter, object, object)

    def __init__(
        self,
        undo_stack: QtGui.QUndoStack = None,
        node_factory: NodeFactory = None,
        parent=None,
    ):
        super().__init__(parent)

        self.node_factory = node_factory or NodeFactory()
        self.undo_stack = undo_stack or QtGui.QUndoStack()

        self.__scene_stack: typing.List[NodeGraphScene] = []
        self.__event_filters: typing.List[SceneEventFilter] = []

        self.pushScene(NodeGraphScene())

    def activeScene(self):
        return self.__scene_stack[-1]

    def rootScene(self):
        return self.__scene_stack[0]

    def reset(self):
        self.__scene_stack.clear()
        self.__event_filters.clear()

        self.pushScene(NodeGraphScene())

    def pushScene(self, scene: NodeGraphScene):
        scene.nodeEdited.connect(self.nodeEdited)
        scene.nodeSelected.connect(self.nodeSelected)
        scene.parameterChanged.connect(self.parameterChanged)

        event_filter = SceneEventFilter(scene, self.undo_stack, self.node_factory)

        self.__scene_stack.append(scene)
        self.__event_filters.append(event_filter)

        self.scenePushed.emit(scene)

    def popScene(self):
        if len(self.__scene_stack) <= 1:
            return

        scene = self.__scene_stack.pop()
        event_filter = self.__event_filters.pop()
        scene.removeEventFilter(event_filter)

        scene.nodeEdited.disconnect(self.nodeEdited)
        scene.nodeSelected.disconnect(self.nodeSelected)
        scene.parameterChanged.disconnect(self.parameterChanged)

        self.scenePushed.emit(self.__scene_stack[-1])

    def attachView(self, view: "NodeGraphView"):
        if self.__scene_stack:
            view.setScene(self.activeScene())

        view.createNodeRequested.connect(self.onNodeCreationRequested)
        view.itemDoubleClicked.connect(self.onItemDoubleClicked)
        self.scenePushed.connect(view.setScene)
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

        action = QtGui.QAction("Group", self)
        action.setData(view)
        action.setShortcut("Ctrl+G")
        action.triggered.connect(self.onGroupActionTriggered)
        view.addAction(action)

        action = QtGui.QAction("ParentGroup", self)
        action.setData(view)
        action.setShortcut("Backspace")
        action.triggered.connect(self.onParentSceneActionTriggered)
        view.addAction(action)

    def createGroup(self, name=None):
        item = self.node_factory.createGroup(name=name)
        cmd = commands.AddItemCommand(self.activeScene(), item)
        cmd.setText(f"Create Group: {item.name()}")
        self.undo_stack.push(cmd)

        return item

    def createNode(self, node_type) -> Node:
        logger.info(f"Creating node of type: {node_type}")
        cmd = commands.CreateNodeCommand(
            self.activeScene(), node_type, self.node_factory
        )
        cmd.setText(f"Create: {node_type}")

        self.undo_stack.push(cmd)
        return cmd.node

    def createBackdrop(self, name):
        backdrop = Backdrop(name)
        cmd = commands.AddItemCommand(self.activeScene(), backdrop)
        cmd.setText("Create Backdrop")
        self.undo_stack.push(cmd)

    def removeItem(self, item):
        cmd = commands.RemoveItemCommand(self.activeScene(), item)
        cmd.setText(f"Remove: {item}")
        self.undo_stack.push(cmd)

    def selectedNodes(self):
        return [n for n in self.activeScene().selectedItems() if isinstance(n, Node)]

    def createConnection(
        self, output_port: OutputPort, input_port: InputPort
    ) -> Connection:
        if not isinstance(output_port, OutputPort):
            raise TypeError(f"Not an output port: {output_port}")

        if not isinstance(input_port, InputPort):
            raise TypeError(f"Not an input port: {input_port}")

        cmd = commands.CreateConnectionCommand(
            self.activeScene(), output_port, input_port
        )
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
        scene_pos = get_scene_position(view)

        hovered_item = self.activeScene().itemAt(scene_pos, QtGui.QTransform())

        if isinstance(hovered_item, Node):
            hovered_item.setViewed(not hovered_item.isViewed())

            for node in self.activeScene().nodes():
                if node is hovered_item:
                    continue
                node.setViewed(False)

    @QtCore.Slot()
    def onEditActionTriggered(self):
        action = self.sender()
        view: "NodeGraphView" = action.data()
        scene_pos = get_scene_position(view)

        modifiers = QtWidgets.QApplication.keyboardModifiers()
        hovered_item = self.activeScene().itemAt(scene_pos, QtGui.QTransform())

        if isinstance(hovered_item, Node):
            hovered_item.setEdited(not hovered_item.isEdited())

        if modifiers & QtCore.Qt.KeyboardModifier.ShiftModifier:
            return

        for node in self.activeScene().nodes():
            if node is hovered_item:
                continue
            node.setEdited(False)

    @QtCore.Slot()
    def onGroupActionTriggered(self):
        action = self.sender()
        view: "NodeGraphView" = action.data()
        scene_pos = get_scene_position(view)
        group = self.createGroup()
        group.setPos(scene_pos)

    @QtCore.Slot(QtWidgets.QGraphicsItem)
    def onItemDoubleClicked(self, item: QtWidgets.QGraphicsItem):
        if isinstance(item, Group):
            self.pushScene(item.subScene())

    @QtCore.Slot()
    def onParentSceneActionTriggered(self):
        self.popScene()


def get_scene_position(view):
    cursor = QtGui.QCursor.pos()
    view_cursor = view.mapFromGlobal(cursor)
    scene_pos = view.mapToScene(view_cursor)
    return scene_pos
