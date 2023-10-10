"""
A custom QGraphicsScene that handles the Node Graph and its interactions.

# TODO: split the tool system into an event filter.
# TODO: add a move tool with a modifier key for grid snapping.
# TODO: move entity creation to a dedicated class e.g. NodeGraphFactory
"""
from PySide6 import QtCore, QtGui, QtWidgets
from radium.nodegraph.dot import Dot
from radium.nodegraph.port import InputPort, OutputPort, Port

from radium.nodegraph.connection import Connection


class PreviewLine(QtWidgets.QGraphicsLineItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 100), 2, QtCore.Qt.PenStyle.DotLine))
        self.setZValue(1000)


class PreviewRect(QtWidgets.QGraphicsRectItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 100), 2, QtCore.Qt.PenStyle.DotLine))
        self.setZValue(1000)


class Tool:
    def __init__(self, scene: "NodeGraphScene"):
        self.scene = scene

    def match(self, event, item):
        return False

    def mousePressEvent(self, event: QtGui.QMouseEvent, item: QtWidgets.QGraphicsItem):
        pass

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        pass

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        pass


class SelectionTool(Tool):
    def __init__(self, scene: "NodeGraphScene"):
        super().__init__(scene)
        self.rect_item = PreviewRect()

        self.pt1 = None
        self.pt2 = None

    def match(self, event, item):
        return event.button() == QtCore.Qt.MouseButton.LeftButton and item is None

    def mousePressEvent(self, event, item):
        self.pt1 = event.scenePos()
        self.pt2 = event.scenePos()
        self.rect_item.setRect(QtCore.QRectF(self.pt1, self.pt2).normalized())
        self.scene.addItem(self.rect_item)
        return True

    def mouseMoveEvent(self, event):
        self.pt2 = event.scenePos()
        self.rect_item.setRect(QtCore.QRectF(self.pt1, self.pt2).normalized())
        return True

    def mouseReleaseEvent(self, event):
        self.scene.removeItem(self.rect_item)
        self.pt2 = event.scenePos()
        rect = QtCore.QRectF(self.pt1, self.pt2).normalized()

        # if shift is not pressed clear selection
        if not event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier:
            self.scene.clearSelection()

        # select all items in rect
        for item in self.scene.items(rect):
            if item.flags() & QtWidgets.QGraphicsItem.ItemIsSelectable:
                item.setSelected(True)

        self.scene.clearTool()
        return True


class ConnectionTool(Tool):
    """
    Handles creation of connections between ports
    """

    def __init__(self, scene: "NodeGraphScene"):
        super().__init__(scene)
        self.preview_line = PreviewLine()
        self.start_port = None

    def match(self, event, item):
        return event.button() == QtCore.Qt.MouseButton.LeftButton and isinstance(item, Port)

    def mousePressEvent(self, event, item: Port):
        self.scene.addItem(self.preview_line)
        self.start_port = item
        self.preview_line.setLine(QtCore.QLineF(self.start_port.scenePos(), event.scenePos()))
        return True

    def mouseMoveEvent(self, event):
        self.preview_line.setLine(QtCore.QLineF(self.start_port.scenePos(), event.scenePos()))
        return True

    def mouseReleaseEvent(self, event):
        self.scene.removeItem(self.preview_line)

        item = self.scene.itemAt(event.scenePos(), QtGui.QTransform())

        if isinstance(item, Port) and item.canConnectTo(self.start_port):
            item.connect(self.start_port)

        elif isinstance(item, Dot):
            if isinstance(self.start_port, InputPort):
                item.output.connect(self.start_port)
            elif isinstance(self.start_port, OutputPort):
                item.input.connect(self.start_port)

        self.scene.clearTool()


class EditConnectionTool(Tool):
    """
    Handles editing of connections.
    """

    def __init__(self, scene: "NodeGraphScene"):
        super().__init__(scene)
        self._start_port = None
        self.preview_line = PreviewLine()

    def match(self, event, item):
        ctrl_pressed = event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier
        return event.button() == QtCore.Qt.MouseButton.LeftButton and isinstance(item, Connection) and not ctrl_pressed

    def mousePressEvent(self, event, item: Connection):
        self.scene.removeItem(item)

        distance_to_input = (event.scenePos() - item.input_port.scenePos()).manhattanLength()
        distance_to_output = (event.scenePos() - item.output_port.scenePos()).manhattanLength()

        if distance_to_input < distance_to_output:
            self._start_port = item.output_port
        else:
            self._start_port = item.input_port

        self.scene.addItem(self.preview_line)
        self.preview_line.setLine(QtCore.QLineF(self._start_port.scenePos(), event.scenePos()))
        return True

    def mouseMoveEvent(self, event):
        self.preview_line.setLine(QtCore.QLineF(self._start_port.scenePos(), event.scenePos()))
        return True

    def mouseReleaseEvent(self, event):
        self.scene.removeItem(self.preview_line)

        end_port: Port = self.scene.itemAt(event.scenePos(), QtGui.QTransform())

        if isinstance(end_port, Port) and end_port.canConnectTo(self._start_port):
            end_port.connect(self._start_port)

        self.scene.clearTool()


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
        return event.button() == QtCore.Qt.MouseButton.LeftButton and isinstance(item, Connection) and ctrl_pressed

    def mousePressEvent(self, event, connection: Connection):
        self.scene.addItem(self.line_1)
        self.scene.addItem(self.line_2)
        self.input_port = connection.input_port
        self.output_port = connection.output_port

        self.line_1.setLine(QtCore.QLineF(self.input_port.scenePos(), event.scenePos()))
        self.line_2.setLine(QtCore.QLineF(event.scenePos(), self.output_port.scenePos()))

        connection.delete()

        return True

    def mouseMoveEvent(self, event):
        self.line_1.setLine(QtCore.QLineF(self.input_port.scenePos(), event.scenePos()))
        self.line_2.setLine(QtCore.QLineF(event.scenePos(), self.output_port.scenePos()))
        return True

    def mouseReleaseEvent(self, event):
        self.scene.removeItem(self.line_1)
        self.scene.removeItem(self.line_2)

        dot = Dot()
        dot.setPos(event.scenePos())
        self.scene.addItem(dot)

        dot.input.connect(self.output_port)
        dot.output.connect(self.input_port)

        self.scene.clearTool()


class NodeGraphScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.tools = [
            SelectionTool(self),
            ConnectionTool(self),
            InsertDotTool(self),
            EditConnectionTool(self),
        ]

        self._grid_size = 10
        self._grid_snap = True

        self._tool = None

    def setGridSize(self, size):
        self._grid_size = size
        self.update()

    def gridSize(self):
        return self._grid_size

    def clearTool(self):
        self._tool = None

    def mousePressEvent(self, event):
        item = self.itemAt(event.scenePos(), QtGui.QTransform())

        for tool in self.tools:
            if tool.match(event, item):
                self._tool = tool
                break

        if self._tool is None:
            return super().mousePressEvent(event)

        return self._tool.mousePressEvent(event, item)

    def mouseMoveEvent(self, event):
        if self._tool is None:
            return super().mouseMoveEvent(event)

        return self._tool.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._tool is None:
            return super().mouseReleaseEvent(event)

        return self._tool.mouseReleaseEvent(event)
