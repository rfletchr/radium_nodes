import typing

from radium.nodegraph.graph.scene.node_base import NodeBase, NodeDataDict
from radium.nodegraph.graph.scene.port import InputPort, OutputPort

if typing.TYPE_CHECKING:
    from radium.nodegraph.factory import NodeFactory


class Node(NodeBase):
    """
    A standard node graph node.
    """

    def __init__(
        self,
        factory: "NodeFactory",
        type_name: str,
        name: str = None,
        parent=None,
    ):
        super().__init__(factory, type_name, name=name, parent=parent)
        self.__inputs: typing.Dict[str, InputPort] = {}
        self.__outputs: typing.Dict[str, OutputPort] = {}

    def inputs(self):
        return self.__inputs.copy()

    def outputs(self):
        return self.__outputs.copy()

    def hasInput(self, name):
        return name in self.__inputs

    def hasOutput(self, name):
        return name in self.__outputs

    def addInput(self, name: str, port_type: str):
        if self.hasInput(name):
            raise ValueError(f"input: {name} already exists")

        port = self.factory().createPort(InputPort, name, port_type)
        self.__inputs[name] = port
        port.setParentItem(self)

    def addOutput(self, name: str, datatype: str):
        if self.hasOutput(name):
            raise ValueError(f"output: {name} already exists")

        port = self.factory().createPort(OutputPort, name, datatype)
        self.__outputs[name] = port
        port.setParentItem(self)
