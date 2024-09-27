"""
A GraphicsItem that represents a port on a node. A port represents a named input or output on a node.
"""

import sys
import typing
import uuid
from PySide6 import QtGui, QtWidgets

if typing.TYPE_CHECKING:
    from radium.nodegraph.factory.prototypes import PortType


class PortDataDict(typing.TypedDict):
    datatype: str
    name: str


class Port(QtWidgets.QGraphicsRectItem):
    def __init__(
        self,
        name: str,
        datatype: str,
        max_connections=None,
        parent=None,
    ):
        super().__init__(parent=parent)
        self.__name = name
        self.__datatype = datatype
        self.__max_connections = 1 if max_connections is None else max_connections
        self.__index = 0

        self.setFlag(self.GraphicsItemFlag.ItemNegativeZStacksBehindParent)
        self.setFlag(self.GraphicsItemFlag.ItemSendsScenePositionChanges)
        self.setRect(-5, -5, 10, 10)

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

    def canConnectTo(self, port):
        if not isinstance(port, InputPort):
            return False

        return super().canConnectTo(port)


class InputPort(Port):
    def __init__(self, name, datatype, parent=None):
        super().__init__(name, datatype, max_connections=1, parent=parent)
        self.setBrush(QtGui.QColor(127, 127, 150))

    def canConnectTo(self, port):
        if not isinstance(port, OutputPort):
            return False

        return super().canConnectTo(port)
