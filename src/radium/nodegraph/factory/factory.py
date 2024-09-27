__all__ = ["NodeFactory"]

import os
import typing
import qtawesome

from PySide6 import QtCore, QtGui
from radium.nodegraph.factory.prototypes import (
    NodeType,
    PortType,
)

from radium.nodegraph.graph.scene.node import Node
from radium.nodegraph.graph.scene.port import InputPort, OutputPort
from radium.nodegraph.factory.model import NodePrototypeModel


class NodeFactory(QtCore.QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__node_types = {}
        self.__port_types = {}
        self.__icon_cache = {}

        self.node_types_model = NodePrototypeModel()

    def registerPortType(self, port_type: PortType, exists_ok=False):
        if port_type.type_name in self.__port_types:
            if not exists_ok:
                raise ValueError(f"Port Type: {port_type.type_name} already registered")

        self.__port_types[port_type.type_name] = port_type

    def registerNodeType(self, prototype: NodeType, exists_ok=False):
        if prototype.type_name in self.__node_types:
            if not exists_ok:
                raise ValueError(f"NodePrototype: {prototype} already registered")
            else:
                self.node_types_model.removePrototype(prototype.type_name)

        self.__node_types[prototype.type_name] = prototype
        self.node_types_model.addPrototype(prototype)

    def hasNodeType(self, name: str) -> bool:
        return name in self.__node_types

    def getNodeType(self, name):
        return self.__node_types[name]

    def hasPortType(self, name: str) -> bool:
        return name in self.__node_types

    def getPortType(self, name):
        return self.__port_types[name]

    def createNodeInstance(self, arg: typing.Union[str, NodeType, dict], **kwargs):
        if isinstance(arg, str):
            prototype = self.getNodeType(arg)
            return Node.fromPrototype(prototype, self, **kwargs)
        elif isinstance(arg, NodeType):
            return Node.fromPrototype(arg, self, **kwargs)
        elif isinstance(arg, dict):
            return Node.fromDict(arg, self)
        else:
            raise ValueError(
                f"expected arg of type str | NodeType | dict got {type(arg)}"
            )

    def createPortInstance(
        self,
        name: str,
        arg: typing.Union[str, NodeType, dict],
        is_input: bool,
    ):

        cls = InputPort if is_input else OutputPort

        if isinstance(arg, str):
            port_type = self.getPortType(arg)
            return cls.fromPrototype(name, port_type)
        elif isinstance(arg, PortType):
            return cls.fromPrototype(name, arg)
        elif isinstance(arg, dict):
            return cls.fromDict(arg)

        raise ValueError(
            f"expected arg of type (str,str) | PortType | dict got {type(arg)}"
        )

    def createParameterInstance(self, arg: typing.Union[str, NodeType, dict]):
        pass

    def createPen(self, data: typing.Tuple):
        members = len(data)
        w = 2.0
        a = 255

        if members == 3:
            r, g, b = data
        elif members == 4:
            r, g, b, a = data
        elif members == 5:
            r, g, b, a, w = data
        else:
            raise ValueError(f"outline must have between 3 and 5 members got: {data}")

        color = QtGui.QColor(r, g, b, a)
        return QtGui.QPen(color, w)

    def createBrush(self, data: typing.Tuple):
        members = len(data)
        a = 255

        if members == 3:
            r, g, b = data
        elif members == 4:
            r, g, b, a = data
        else:
            raise ValueError(f"outline must have between 3 and 4 members got: {data}")

        color = QtGui.QColor(r, g, b, a)
        return QtGui.QBrush(color)

    def createIcon(self, icon_str: str):
        if os.path.exists(icon_str):
            return QtGui.QIcon(icon_str)
        else:
            return qtawesome.icon(icon_str)
