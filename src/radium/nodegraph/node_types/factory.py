__all__ = ["NodeFactory"]

import typing

from PySide6 import QtCore
from radium.nodegraph.node_types.prototypes import (
    NodeType,
    PortType,
)

from radium.nodegraph.graph.scene.node import Node
from radium.nodegraph.graph.scene.port import InputPort, OutputPort
from radium.nodegraph.node_types.model import NodePrototypeModel


class NodeFactory(QtCore.QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__node_types = {}
        self.__port_types = {}
        self.node_types_model = NodePrototypeModel()

    def registerPortType(self, port_type: PortType, exists_ok=False):
        if port_type.port_type in self.__port_types:
            if not exists_ok:
                raise ValueError(f"Port Type: {port_type.port_type} already registered")

        self.__port_types[port_type.port_type] = port_type

    def registerNodeType(self, prototype: NodeType, exists_ok=False):
        if prototype.node_type in self.__node_types:
            if not exists_ok:
                raise ValueError(f"NodePrototype: {prototype} already registered")
            else:
                self.node_types_model.removePrototype(prototype.node_type)

        self.__node_types[prototype.node_type] = prototype
        self.node_types_model.addPrototype(prototype)

    def getNodeType(self, name):
        return self.__node_types[name]

    def getPortType(self, name):
        return self.__port_types[name]

    def createNodeInstance(self, arg: typing.Union[str, NodeType, dict]):
        if isinstance(arg, str):
            prototype = self.getNodeType(arg)
            return Node.fromPrototype(prototype, self)
        elif isinstance(arg, NodeType):
            return Node.fromPrototype(arg, self)
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
