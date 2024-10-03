__all__ = ["NodeFactory"]

import os
import typing
import uuid

import qtawesome

from PySide6 import QtCore, QtGui
from radium.nodegraph.factory.prototypes import (
    NodeType,
    PortType,
)

from radium.nodegraph.graph.scene.node import Node, NodeDataDict
from radium.nodegraph.graph.scene.port import PortDataDict, Port
from radium.nodegraph.factory.model import NodePrototypeModel
from radium.nodegraph.parameters.parameter import Parameter, ParameterDataDict


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

    def getNodeType(self, name) -> NodeType:
        return self.__node_types.get(name)

    def hasPortType(self, name: str) -> bool:
        return name in self.__node_types

    def getPortType(self, name):
        return self.__port_types.get(name)

    def cloneNode(self, node: Node) -> Node:
        data = node.toDict()
        data["unique_id"] = uuid.uuid4().hex
        return self.createNode(node.nodeType(), data=data)

    def createNode(self, node_type_name: str, data: NodeDataDict = None):
        node_type = self.getNodeType(node_type_name)

        if node_type is None:
            if "/" in node_type_name:
                name = node_type_name[node_type_name.rindex("/") :]
            else:
                name = node_type_name
        else:
            name = node_type.name

        instance = Node(self, node_type_name, name=name)

        if node_type is not None:
            applyItemStyle(node_type, instance)

            for name, datatype in node_type.inputs.items():
                instance.addInput(name, datatype)

            for name, datatype in node_type.outputs.items():
                instance.addOutput(name, datatype)

            for name, prototype in node_type.parameters.items():
                if prototype.datatype is None:
                    default = prototype.value
                else:
                    default = prototype.default

                instance.addParameter(
                    name,
                    prototype.datatype,
                    prototype.value,
                    default,
                    **prototype.metadata,
                )

        if data:
            instance.loadDict(data)

        return instance

    def createPort(
        self, cls: typing.Type[Port], name, port_type: str, data: PortDataDict = None
    ):
        instance = cls(name, port_type)

        port_type = self.getPortType(port_type)
        if port_type is not None:
            applyItemStyle(port_type, instance)

        if data:
            instance.loadDict(data)

        return instance

    def createParameter(
        self, name, datatype, value, default, metadata, data: ParameterDataDict = None
    ):
        default = default if default is None else value
        instance = Parameter(name, datatype, value, default, **metadata)

        if data:
            instance.loadDict(data)

        return instance


def applyItemStyle(type_class: typing.Union["NodeType", "PortType"], item):
    pen = createPen(type_class.outline_color)
    brush = createBrush(type_class.color)
    item.setPen(pen)
    item.setBrush(brush)


def createPen(data: typing.Tuple):
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


def createBrush(data: typing.Tuple):
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


def createIcon(icon_str: str):
    if os.path.exists(icon_str):
        return QtGui.QIcon(icon_str)
    else:
        return qtawesome.icon(icon_str)
