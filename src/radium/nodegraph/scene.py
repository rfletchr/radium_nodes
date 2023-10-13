"""
A custom QGraphicsScene that handles the Node Graph and its interactions.

# TODO: add a move tool with a modifier key for grid snapping.
"""
import re
import typing
from PySide6 import QtCore, QtGui, QtWidgets
from radium.nodegraph.node import Node
from radium.nodegraph.dot import Dot
from radium.nodegraph.port import InputPort, OutputPort, Port

from radium.nodegraph.connection import Connection


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
    def __init__(self, controller: "NodeGraphSceneController"):
        self.controller = controller

    def match(self, event, item):
        """
        Return True if the tool should be used for the given event and item.
        """
        return False

    def mousePressEvent(self, event: QtGui.QMouseEvent, item: QtWidgets.QGraphicsItem):
        pass

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        pass

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        pass


class SelectionTool(Tool):
    def __init__(self, controller: "NodeGraphSceneController"):
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
            if item.flags() & QtWidgets.QGraphicsItem.ItemIsSelectable:
                item.setSelected(True)

        self.controller.clearTool()
        return True


class ConnectionTool(Tool):
    """
    Handles creation of connections between ports
    """

    def __init__(self, controller: "NodeGraphSceneController"):
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

        if isinstance(scene_item, Port) and scene_item.canConnectTo(self.start_port):
            end_port = scene_item

        # here dots are a special case as they're a bit finicky to click on. If the user releases the mouse
        # on a dot, we'll try to connect to the dot's input or output port depending on the start port.
        elif isinstance(scene_item, Dot):
            if isinstance(self.start_port, InputPort):
                end_port = scene_item.output
            elif isinstance(self.start_port, OutputPort):
                end_port = scene_item.input
            else:
                end_port = None
        else:
            end_port = None

        if end_port is None:
            return False

        self.controller.createConnection(self.start_port, end_port)
        self.controller.clearTool()
        return True


class EditConnectionTool(Tool):
    """
    Handles editing of connections.
    """

    def __init__(self, controller: "NodeGraphSceneController"):
        super().__init__(controller)
        self._start_port = None
        self.preview_line = PreviewLine()

    def match(self, event, item):
        ctrl_pressed = event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier
        left_mouse_clicked = event.button() == QtCore.Qt.MouseButton.LeftButton
        is_connection = isinstance(item, Connection)

        return left_mouse_clicked and is_connection and not ctrl_pressed

    def mousePressEvent(self, event, item: Connection):
        self.controller.scene.removeItem(item)

        distance_to_input = (
            event.scenePos() - item.input_port.scenePos()
        ).manhattanLength()
        distance_to_output = (
            event.scenePos() - item.output_port.scenePos()
        ).manhattanLength()

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
        self.controller.scene.removeItem(self.preview_line)

        end_port: Port = self.controller.scene.itemAt(
            event.scenePos(), QtGui.QTransform()
        )

        if isinstance(end_port, Port) and end_port.canConnectTo(self._start_port):
            self.controller.createConnection(self._start_port, end_port)

        self.controller.clearTool()
        return True


class InsertDotTool(Tool):
    """
    Handles creation of dots
    """

    def __init__(self, scene: "NodeGraphScene"):
        super().__init__(scene)
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

        connection.delete()

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
        self.controller.scene.addItem(dot)

        self.controller.createConnection(dot.input, self.output_port)
        self.controller.createConnection(self.input_port, dot.output)

        self.controller.clearTool()
        return True


class ShiftDragCloneTool(Tool):
    """
    Handles cloning of nodes when shift dragging.
    """

    def __init__(self, scene: "NodeGraphScene"):
        super().__init__(scene)
        self.preview_rect = PreviewRect()
        self.preview_rect.setBrush(QtGui.QColor(0, 0, 0, 64))

        self.dragged_node: Node = None

    def match(self, event, item):
        return (
            event.button() == QtCore.Qt.MouseButton.LeftButton
            and event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier
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
        new_node = self.controller.duplicateNode(self.dragged_node)
        new_node.setPos(event.scenePos())
        self.dragged_node = None
        self.controller.scene.removeItem(self.preview_rect)
        self.controller.clearTool()
        return True


class NodeGraphSceneController(QtCore.QObject):
    def __init__(self, scene: QtWidgets.QGraphicsScene, tools=None, parent=None):
        super().__init__(parent=parent)
        self.scene = scene
        self.scene.installEventFilter(self)

        self.tools: typing.List[Tool] = tools or [
            SelectionTool(self),
            ConnectionTool(self),
            InsertDotTool(self),
            EditConnectionTool(self),
            ShiftDragCloneTool(self),
        ]

        self._tool: Tool = None

    def createNode(self, name, inputs, outputs):
        node = Node(name, inputs, outputs)
        self.scene.addItem(node)
        return node

    def createDot(self, position=None):
        dot = Dot()
        self.scene.addItem(dot)

        if position is not None:
            dot.setPos(position)

        return dot

    def createConnection(self, port_a: Port, port_b: Port):
        input_port = port_a if isinstance(port_a, InputPort) else port_b
        output_port = port_a if isinstance(port_a, OutputPort) else port_b
        connection = Connection(input_port, output_port)
        self.scene.addItem(connection)

    def duplicateNode(self, node: Node):
        new_name = self.uniqueNodeName(node.name())
        new_node = Node(new_name, node.inputs.keys(), node.outputs.keys())
        new_node.setPos(node.pos() + QtCore.QPointF(10, 10))
        self.scene.addItem(new_node)
        return new_node

    def uniqueNodeName(self, name):
        existing_names = [
            item.name() for item in self.scene.items() if isinstance(item, Node)
        ]
        if name not in existing_names:
            return name

        name_without_suffix = re.sub(r"(_)?\d+$", "", name)

        i = 1
        while True:
            new_name = f"{name_without_suffix}_{i:02d}"
            if new_name not in existing_names:
                return new_name
            i += 1

    def clearTool(self):
        self._tool = None

    def eventFilter(self, scene, event):
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
