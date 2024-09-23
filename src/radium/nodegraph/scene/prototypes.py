__all__ = ["ParameterPrototype", "PortPrototype", "NodePrototype"]
import typing


class ParameterPrototype(typing.NamedTuple):
    name: str
    default: typing.Any


class PortPrototype(typing.NamedTuple):
    name: str
    datatype: str


class NodePrototype(typing.NamedTuple):
    node_type: str
    parameters: typing.Tuple[ParameterPrototype, ...]
    inputs: typing.Tuple[PortPrototype, ...]
    outputs: typing.Tuple[PortPrototype, ...]
