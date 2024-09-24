"""
A GraphicsItem that represents a port on a node. A port represents a named input or output on a node.
"""

import sys
import uuid
from PySide6 import QtGui, QtWidgets
from radium.nodegraph.graph.scene.prototypes import PortPrototype


class Port(QtWidgets.QGraphicsRectItem):
    def __init__(
        self, name: str, datatype: str, unique_id=None, max_connections=1, parent=None
    ):
        super().__init__(parent=parent)
        self.__name = name
        self.__datatype = datatype
        self.__max_connections = max_connections
        self._unique_id = unique_id or uuid.uuid4().hex
        self.setFlag(self.GraphicsItemFlag.ItemNegativeZStacksBehindParent)
        self.setFlag(self.GraphicsItemFlag.ItemSendsScenePositionChanges)
        self.setRect(-5, -5, 10, 10)

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
        return self._unique_id

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
        return {
            "datatype": self.datatype(),
            "name": self.name(),
            "unique_id": self.uniqueId(),
        }

    @classmethod
    def fromDict(cls, data):
        return cls(data["name"], data["datatype"], data["unique_id"])

    @classmethod
    def fromPrototype(cls, prototype: "PortPrototype"):
        return cls(prototype.name, prototype.datatype)


class OutputPort(Port):
    def __init__(self, name, datatype, unique_id=None, parent=None):
        super().__init__(
            name,
            datatype,
            max_connections=sys.maxsize,
            unique_id=unique_id,
            parent=parent,
        )
        self.setBrush(QtGui.QColor(64, 64, 64))

    def canConnectTo(self, port):
        if not isinstance(port, InputPort):
            return False

        return super().canConnectTo(port)


class InputPort(Port):
    def __init__(self, name, datatype, unique_id=None, parent=None):
        super().__init__(
            name, datatype, max_connections=1, unique_id=unique_id, parent=parent
        )
        self.setBrush(QtGui.QColor(127, 127, 150))

    def canConnectTo(self, port):
        if not isinstance(port, OutputPort):
            return False

        return super().canConnectTo(port)
