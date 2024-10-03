"""
A GraphicsItem that represents a port on a node. A port represents a named input or output on a node.
"""

import qtawesome
import sys
import typing
from PySide6 import QtGui, QtWidgets, QtCore

if typing.TYPE_CHECKING:
    from radium.nodegraph.factory.prototypes import PortType


class PortDataDict(typing.TypedDict):
    datatype: str
    name: str


class Port(QtWidgets.QGraphicsItem):
    def __init__(
        self,
        name: str,
        datatype: str,
        max_connections=None,
        parent=None,
    ):
        super().__init__(parent=parent)
        self.__index = 0
        self.__name = name
        self.__pen = QtGui.QPen()
        self.__brush = QtGui.QBrush()
        self.__datatype = datatype
        self.__max_connections = 1 if max_connections is None else max_connections

        self.setFlag(self.GraphicsItemFlag.ItemNegativeZStacksBehindParent)
        self.setFlag(self.GraphicsItemFlag.ItemSendsScenePositionChanges)
        self.setZValue(-1)

    def brush(self):
        return self.__brush

    def setBrush(self, brush):
        self.__brush = brush

    def pen(self):
        return self.__pen

    def setPen(self, pen):
        self.__pen = pen

    def setIndex(self, index: int):
        self.__index = index

    def index(self) -> int:
        return self.__index

    def itemChange(self, change: QtWidgets.QGraphicsItem.GraphicsItemChange, value):
        if (
            change
            == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemScenePositionHasChanged
        ):
            scene = self.scene()
            if hasattr(scene, "updatePortConnections"):
                scene.updatePortConnections(self)

        return super().itemChange(change, value)

    def maxConnections(self):
        return self.__max_connections

    def connections(self):
        return self.scene().getConnections(self)

    def uniqueId(self):
        return self.__unique_id

    def node(self):
        return self.parentItem()

    def canConnectTo(self, port: "Port"):
        if port is self:
            return False

        if port.parentItem() is self.parentItem():
            return False

        return True

    def datatype(self):
        return self.__datatype

    def name(self):
        return self.__name

    def toDict(self):
        return PortDataDict(
            datatype=self.__datatype,
            name=self.__name,
        )

    def loadDict(self, data: PortDataDict):
        self.__name = data["name"]
        self.__datatype = data["datatype"]

    @classmethod
    def fromPrototype(
        cls,
        name,
        port_type: "PortType",
    ):
        instance = cls(name, port_type.type_name)
        return instance


class OutputPort(Port):
    def __init__(self, name, datatype, parent=None):
        super().__init__(
            name,
            datatype,
            max_connections=sys.maxsize,
            parent=parent,
        )
        self.setBrush(QtGui.QColor(64, 64, 64))
        self.__bounding_rect = QtCore.QRectF(-10, -6, 20, 12)

    def boundingRect(self):
        return self.__bounding_rect

    def canConnectTo(self, port):
        if not isinstance(port, InputPort):
            return False

        return super().canConnectTo(port)

    def paint(self, painter, option, widget=None):
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(self.brush())
        radius = self.boundingRect().width() / 2

        painter.drawRoundedRect(self.__bounding_rect, radius, radius)
        box_rect = self.__bounding_rect.adjusted(
            0,
            -self.__bounding_rect.height() * 0.5,
            0,
            -self.__bounding_rect.height() * 0.5,
        )
        painter.drawRect(box_rect)

        painter.setPen(self.pen())
        start_angle = 180 * 16  # Starting at 0 degrees
        span_angle = 180 * 16  # 180 degrees span for half circle
        painter.drawArc(self.__bounding_rect, start_angle, span_angle)
        painter.drawLine(box_rect.topLeft(), box_rect.bottomLeft())
        painter.drawLine(box_rect.topRight(), box_rect.bottomRight())


class InputPort(Port):
    def __init__(self, name, datatype, parent=None):
        super().__init__(name, datatype, max_connections=1, parent=parent)
        self.setBrush(QtGui.QColor(127, 127, 150))
        self.__bounding_rect = QtCore.QRectF(-10, -6, 20, 12)

    def canConnectTo(self, port):
        if not isinstance(port, OutputPort):
            return False

        return super().canConnectTo(port)

    def boundingRect(self):
        return self.__bounding_rect

    def paint(self, painter, option, widget=None):
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(self.brush())
        radius = self.boundingRect().width() / 2

        painter.drawRoundedRect(self.__bounding_rect, radius, radius)

        box_rect = self.__bounding_rect.adjusted(
            0,
            self.__bounding_rect.height() * 0.5,
            0,
            self.__bounding_rect.height() * 0.5,
        )
        painter.drawRect(box_rect)

        painter.setPen(self.pen())
        start_angle = 0 * 16  # Starting at 0 degrees
        span_angle = 180 * 16  # 180 degrees span for half circle
        painter.drawArc(self.__bounding_rect, start_angle, span_angle)
        painter.drawLine(box_rect.topLeft(), box_rect.bottomLeft())
        painter.drawLine(box_rect.topRight(), box_rect.bottomRight())
