"""
A GraphicsItem that represents a port on a node. A port represents a named input or output on a node.
"""
import typing
from PySide6 import QtGui, QtWidgets

from radium.nodegraph.connection import Connection


class Port(QtWidgets.QGraphicsPathItem):
    def __init__(self, name, parent=None):
        super().__init__(parent=parent)
        self.name = name
        self._connections: typing.List["Connection"] = []
        self.setFlag(self.GraphicsItemFlag.ItemSendsScenePositionChanges)
        self.setFlag(self.GraphicsItemFlag.ItemNegativeZStacksBehindParent)

        self.setZValue(-1)

    def node(self):
        return self.parentItem()

    def itemChange(self, change, value):
        for connection in self._connections:
            connection.layout()

        return super().itemChange(change, value)

    def canConnectTo(self, port: "Port"):
        if port is self:
            return False

        if port.parentItem() is self.parentItem():
            return False

        return True

    def disconnectAll(self):
        for connection in self._connections.copy():
            connection.delete()

    def registerConnection(self, connection: "Connection"):
        self._connections.append(connection)

    def unRegisterConnection(self, connection: "Connection"):
        self._connections.remove(connection)

    def connect(self, port: "Port") -> Connection:
        raise NotImplementedError()


class OutputPort(Port):
    def __init__(self, name, parent=None):
        super().__init__(name, parent=parent)
        self.setBrush(QtGui.QColor(64, 64, 64))
        path = QtGui.QPainterPath()
        path.addRect(-5, -5, 10, 10)
        self.setPath(path)

    def canConnectTo(self, port):
        if not isinstance(port, InputPort):
            return False

        return super().canConnectTo(port)

    def connect(self, port: "InputPort"):
        if not self.canConnectTo(port):
            raise ValueError(f"Cannot connect to port: {port}")

        self.scene().addItem(Connection(input_port=port, output_port=self))


class InputPort(Port):
    def __init__(self, name, parent=None):
        super().__init__(name, parent=parent)
        self.setBrush(QtGui.QColor(127, 127, 150))
        path = QtGui.QPainterPath()
        path.addRect(-5, -5, 10, 10)
        self.setPath(path)

    def canConnectTo(self, port):
        if not isinstance(port, OutputPort):
            return False

        return super().canConnectTo(port)

    def connect(self, port: "OutputPort"):
        if not self.canConnectTo(port):
            raise ValueError(f"Cannot connect to port: {port}")

        self.scene().addItem(Connection(input_port=self, output_port=port))
