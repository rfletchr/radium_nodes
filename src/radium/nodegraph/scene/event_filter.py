"""
An event filter for handling node graph interactions. Each interaction is defined by a Tool e.g. Selection, Connection.

"""

import typing
import uuid

from PySide6 import QtCore, QtGui, QtWidgets
from radium.nodegraph.scene.node import Node
from radium.nodegraph.scene.dot import Dot
from radium.nodegraph.scene.connection import Connection
from radium.nodegraph.scene.port import InputPort, OutputPort, Port
from radium.nodegraph.scene import commands

if typing.TYPE_CHECKING:
    from radium.nodegraph.scene.scene import NodeGraphScene


def sort_ports(a, b):
    if isinstance(b, InputPort) and isinstance(a, OutputPort):
        return a, b
    elif isinstance(b, OutputPort) and isinstance(a, InputPort):
        return b, a

    raise TypeError(f"expected an input and an output port got: {a} & {b}")


def get_nearby_port(node: Node, pos: QtCore.QPointF, port_type):
    """
    Returns the port closest to the given position.
    """
    if issubclass(port_type, InputPort):
        ports = node.inputs.values()
    elif issubclass(port_type, OutputPort):
        ports = node.outputs.values()
    else:
        raise TypeError("port_type must be subclass of InputPort, OutputPort")

    closest_port = None
    closest_distance = 100000

    for port in ports:
        distance = (port.scenePos() - pos).manhattanLength()
        if distance < closest_distance:
            closest_distance = distance
            closest_port = port

    return closest_port


def get_potential_port(
    port: Port, item: typing.Union[Port, Dot, Node], event_pos: QtCore.QPointF
):
    """
    A utility function that tries to return a port from the given item.

    Args:
        port: The port that is being connected to.
        item: The item that is being connected to.
        event_pos: The position of the mouse event this is used to determine
            the closest port if the item is a node.
    """
    if not isinstance(port, (InputPort, OutputPort)):
        raise TypeError("port must be an instance of InputPort or OutputPort")

    if not isinstance(item, (Port, Dot, Node)):
        raise TypeError("item must be an instance of Port, Dot or Node")

    if isinstance(item, Port):
        return item

    elif isinstance(item, Dot):
        if isinstance(port, InputPort):
            return item.output
        else:
            return item.input

    else:  # else it is a Node
        if isinstance(port, InputPort):
            return get_nearby_port(item, event_pos, OutputPort)
        else:
            return get_nearby_port(item, event_pos, InputPort)


class PreviewLine(QtWidgets.QGraphicsLineItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPen(
            QtGui.QPen(QtGui.QColor(0, 0, 0, 100), 2, QtCore.Qt.PenStyle.DotLine)
        )
        self.setZValue(1000)


class PreviewRect(QtWidgets.QGraphicsRectItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPen(
            QtGui.QPen(QtGui.QColor(0, 0, 0, 100), 2, QtCore.Qt.PenStyle.DotLine)
        )
        self.setZValue(1000)


class Tool:
    def __init__(self, controller: "SceneEventFilter"):
        self.controller = controller

    def match(self, event, item):
        """
        Return True if the tool should be used for the given event and item.
        """
        return False

    def mousePressEvent(
        self,
        event: QtWidgets.QGraphicsSceneMouseEvent,
        item: QtWidgets.QGraphicsItem,
    ):
        pass

    def mouseMoveEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        pass

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        pass


class BoxSelectionTool(Tool):
    """
    Handles:
        - dragging a box to select multiple nodegraph.
    """

    def __init__(self, controller: "SceneEventFilter"):
        super().__init__(controller)
        self.preview_rect = PreviewRect()

        self.pt1 = None
        self.pt2 = None

    def match(self, event, item):
        return event.button() == QtCore.Qt.MouseButton.LeftButton and item is None

    def mousePressEvent(self, event, item):
        self.pt1 = event.scenePos()
        self.pt2 = event.scenePos()
        self.preview_rect.setRect(QtCore.QRectF(self.pt1, self.pt2).normalized())
        self.controller.scene.addItem(self.preview_rect)
        return True

    def mouseMoveEvent(self, event):
        self.pt2 = event.scenePos()
        self.preview_rect.setRect(QtCore.QRectF(self.pt1, self.pt2).normalized())
        return True

    def mouseReleaseEvent(self, event):
        self.controller.scene.removeItem(self.preview_rect)
        self.pt2 = event.scenePos()
        rect = QtCore.QRectF(self.pt1, self.pt2).normalized()

        # if shift is not pressed clear selection
        if not event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier:
            self.controller.scene.clearSelection()

        # select all items in rect
        for item in self.controller.scene.items(rect):
            if item.flags() & QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable:
                item.setSelected(True)

        self.controller.clearTool()
        return True


class ConnectionTool(Tool):
    """
    Handles:
        - dragging between 2 ports to make a connection.
    """

    def __init__(self, controller: "SceneEventFilter"):
        super().__init__(controller)
        self.preview_line: PreviewLine = PreviewLine()
        self.start_port = None

    def match(self, event, item):
        left_button_clicked = event.button() == QtCore.Qt.MouseButton.LeftButton
        item_is_port = isinstance(item, Port)
        return left_button_clicked and item_is_port

    def mousePressEvent(self, event, item: Port):
        """
        begin drawing a preview line from the given port
        """
        self.controller.scene.addItem(self.preview_line)
        self.start_port = item
        self.preview_line.setLine(
            QtCore.QLineF(self.start_port.scenePos(), event.scenePos())
        )
        return True

    def mouseMoveEvent(self, event):
        """
        update the end point of the preview line
        """
        self.preview_line.setLine(
            QtCore.QLineF(self.start_port.scenePos(), event.scenePos())
        )
        return True

    def mouseReleaseEvent(self, event):
        """
        if the preview line ends on a port or a dot, create an appropriate connection.
        """
        self.controller.scene.removeItem(self.preview_line)

        scene_item = self.controller.scene.itemAt(event.scenePos(), QtGui.QTransform())

        if isinstance(scene_item, (Port, Dot, Node)):
            end_port = get_potential_port(self.start_port, scene_item, event.scenePos())
            if end_port.canConnectTo(self.start_port):
                output_port, input_port = sort_ports(self.start_port, end_port)

                cmd = commands.CreateConnectionCommand(
                    self.controller.scene, output_port, input_port
                )
                self.controller.undo_stack.push(cmd)

        self.controller.clearTool()
        return True


class EditConnectionTool(Tool):
    """
    Handles:
        - dragging a connection to disconnect it.
        - dragging a connection to move it to another port.
    """

    def __init__(self, controller: "SceneEventFilter"):
        super().__init__(controller)
        self._start_port = None
        self.preview_line = PreviewLine()

    def match(self, event, item):
        ctrl_pressed = event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier
        left_mouse_clicked = event.button() == QtCore.Qt.MouseButton.LeftButton
        is_connection = isinstance(item, Connection)

        return left_mouse_clicked and is_connection and not ctrl_pressed

    def mousePressEvent(self, event, item: Connection):
        self.controller.undo_stack.beginMacro("Edit Connection")
        self.controller.undo_stack.push(
            commands.RemoveItemCommand(self.controller.scene, item)
        )

        # get the distance to the input and output ports
        distance_to_input = (
            event.scenePos() - item.input_port.scenePos()
        ).manhattanLength()
        distance_to_output = (
            event.scenePos() - item.output_port.scenePos()
        ).manhattanLength()

        # set the start port to the furthest port, conceptually your disconnecting
        # the closest port.
        if distance_to_input < distance_to_output:
            self._start_port = item.output_port
        else:
            self._start_port = item.input_port

        self.controller.scene.addItem(self.preview_line)
        self.preview_line.setLine(
            QtCore.QLineF(self._start_port.scenePos(), event.scenePos())
        )
        return True

    def mouseMoveEvent(self, event):
        self.preview_line.setLine(
            QtCore.QLineF(self._start_port.scenePos(), event.scenePos())
        )
        return True

    def mouseReleaseEvent(self, event):
        try:
            self.controller.scene.removeItem(self.preview_line)

            scene_item = self.controller.scene.itemAt(
                event.scenePos(), QtGui.QTransform()
            )

            if isinstance(scene_item, (Port, Dot, Node)):
                end_port = get_potential_port(
                    self._start_port, scene_item, event.scenePos()
                )

                if end_port.canConnectTo(self._start_port):
                    output_port, input_port = sort_ports(end_port, self._start_port)

                    cmd = commands.CreateConnectionCommand(
                        self.controller.scene, output_port, input_port
                    )
                    self.controller.undo_stack.push(cmd)

            self.controller.undo_stack.endMacro()
        finally:
            self.controller.clearTool()
        return True


class InsertDotTool(Tool):
    """
    Handles creation of dots
    """

    def __init__(self, controller: "SceneEventFilter"):
        super().__init__(controller)
        self.line_1 = PreviewLine()
        self.line_2 = PreviewLine()
        self.input_port = None
        self.output_port = None

    def match(self, event, item):
        ctrl_pressed = event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier
        left_mouse_clicked = event.button() == QtCore.Qt.MouseButton.LeftButton
        is_connection = isinstance(item, Connection)
        return left_mouse_clicked and is_connection and ctrl_pressed

    def mousePressEvent(self, event, connection: Connection):
        """
        - draw a preview line from the connections input to the mouse position
        - draw a preview line from the mouse position to the connections output
        - delete the connection
        """

        self.controller.scene.addItem(self.line_1)
        self.controller.scene.addItem(self.line_2)

        self.input_port = connection.input_port
        self.output_port = connection.output_port

        self.line_1.setLine(QtCore.QLineF(self.input_port.scenePos(), event.scenePos()))
        self.line_2.setLine(
            QtCore.QLineF(event.scenePos(), self.output_port.scenePos())
        )

        self.controller.undo_stack.beginMacro("Insert Dot")
        cmd = commands.RemoveItemCommand(self.controller.scene, connection)
        self.controller.undo_stack.push(cmd)

        return True

    def mouseMoveEvent(self, event):
        """
        update the preview lines
        """
        self.line_1.setLine(QtCore.QLineF(self.input_port.scenePos(), event.scenePos()))
        self.line_2.setLine(
            QtCore.QLineF(event.scenePos(), self.output_port.scenePos())
        )
        return True

    def mouseReleaseEvent(self, event):
        """
        create a dot at the mouse position and connect it to the input and output ports
        """
        self.controller.scene.removeItem(self.line_1)
        self.controller.scene.removeItem(self.line_2)

        dot = Dot()
        dot.setPos(event.scenePos())
        self.controller.undo_stack.push(
            commands.AddItemCommand(self.controller.scene, dot)
        )
        self.controller.undo_stack.push(
            commands.CreateConnectionCommand(
                self.controller.scene, self.output_port, dot.input
            )
        )
        self.controller.undo_stack.push(
            commands.CreateConnectionCommand(
                self.controller.scene, dot.output, self.input_port
            )
        )
        self.controller.undo_stack.endMacro()
        self.controller.clearTool()
        return True


class AltDragCloneTool(Tool):
    """
    Handles cloning of nodegraph when shift dragging.
    """

    def __init__(self, controller: "SceneEventFilter"):
        super().__init__(controller)
        self.preview_rect = PreviewRect()
        self.preview_rect.setBrush(QtGui.QColor(0, 0, 0, 64))

        self.dragged_node: typing.Optional[Node] = None

    def match(self, event, item):
        return (
            event.button() == QtCore.Qt.MouseButton.LeftButton
            and event.modifiers() & QtCore.Qt.KeyboardModifier.AltModifier
            and isinstance(item, Node)
        )

    def mousePressEvent(self, event, item):
        self.dragged_node = item
        self.preview_rect.setRect(item.boundingRect())
        self.preview_rect.setPos(item.pos())
        self.controller.scene.addItem(self.preview_rect)
        return True

    def mouseMoveEvent(self, event):
        """
        - move the preview rect to the mouse position
        """
        self.preview_rect.setPos(event.scenePos())

        return True

    def mouseReleaseEvent(self, event):
        """ """
        cmd = commands.CloneNodeCommand(
            self.controller.scene, self.dragged_node, position=event.scenePos()
        )
        self.controller.undo_stack.push(cmd)
        self.dragged_node = None
        self.controller.scene.removeItem(self.preview_rect)
        self.controller.clearTool()
        return True


class SelectAndMoveTool(Tool):
    def __init__(self, controller: "SceneEventFilter"):
        super().__init__(controller)
        self.nodes: typing.Set[Node] = set()
        self.drag_start: QtCore.QPointF = QtCore.QPointF(0, 0)
        self.drag_id: typing.Optional[str] = None

    def match(self, event, item):
        return event.button() == QtGui.Qt.MouseButton.LeftButton and isinstance(
            item, Node
        )

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent, item: Node):
        self.drag_id = uuid.uuid4().hex

        selected = {
            n for n in item.scene().items() if isinstance(n, Node) and n.isSelected()
        }

        shift_pressed = event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier

        if shift_pressed:
            self.nodes = selected
            item.setSelected(True)
            selected.add(item)
        else:
            for node in selected:
                node.setSelected(False)
            item.setSelected(True)
            self.nodes = {item}

        self.drag_start = event.scenePos()
        return True

    def mouseMoveEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        delta = event.scenePos() - self.drag_start
        self.drag_start = event.scenePos()
        cmd = commands.MoveNodesCommand(self.nodes, delta, self.drag_id)
        self.controller.undo_stack.push(cmd)

        return True

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        self.nodes = set()
        self.drag_start = QtCore.QPointF(0, 0)
        self.controller.clearTool()
        return True


class SceneEventFilter(QtCore.QObject):
    """
    An event filter that reacts to QGraphicsSceneEvent events.

    Interactions are matched to a tool and then subsequent events are passed to that tool until it completes.

    """

    def __init__(
        self, scene: "NodeGraphScene", undo_stack: QtGui.QUndoStack, parent=None
    ):
        super().__init__(parent=parent)
        self.scene = scene
        self.undo_stack = undo_stack
        self.scene.installEventFilter(self)

        self.tools: typing.List[Tool] = [
            BoxSelectionTool(self),
            ConnectionTool(self),
            InsertDotTool(self),
            EditConnectionTool(self),
            AltDragCloneTool(self),
            SelectAndMoveTool(self),
        ]

        self._tool: typing.Optional[Tool] = None

    def clearTool(self):
        self._tool = None

    def eventFilter(self, scene, event: QtWidgets.QGraphicsSceneMouseEvent):
        if scene is not self.scene:
            return False

        if event.type() == QtCore.QEvent.Type.GraphicsSceneMousePress:
            return self.mousePressEvent(event)
        elif event.type() == QtCore.QEvent.Type.GraphicsSceneMouseMove:
            return self.mouseMoveEvent(event)
        elif event.type() == QtCore.QEvent.Type.GraphicsSceneMouseRelease:
            return self.mouseReleaseEvent(event)

        return False

    def mousePressEvent(self, event):
        item = self.scene.itemAt(event.scenePos(), QtGui.QTransform())

        for tool in self.tools:
            if tool.match(event, item):
                self._tool = tool
                break

        if self._tool is None:
            return False

        return self._tool.mousePressEvent(event, item)

    def mouseMoveEvent(self, event):
        if self._tool is None:
            return False

        return self._tool.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._tool is None:
            return False

        return self._tool.mouseReleaseEvent(event)
