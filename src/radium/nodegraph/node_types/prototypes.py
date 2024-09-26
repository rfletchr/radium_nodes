__all__ = ["ParameterPrototype", "NodeType", "PortType"]
import typing
import dataclasses
from PySide6 import QtCore, QtGui


@dataclasses.dataclass(frozen=True)
class ParameterPrototype:
    name: str
    default: typing.Any


# @dataclasses.dataclass(frozen=True)
# class PortPrototype:
#     name: str
#     datatype: str


class PortTypePathDict(typing.TypedDict):
    input: QtGui.QPainterPath
    output: QtGui.QPainterPath


@dataclasses.dataclass(frozen=True)
class PortType:
    port_type: str
    pen: QtGui.QPen
    brush: QtGui.QBrush
    path: typing.Union[QtGui.QPainterPath, PortTypePathDict, None] = None


@dataclasses.dataclass(frozen=True)
class NodeType:
    name: str
    category: str = "Nodes"
    parameters: typing.Tuple[ParameterPrototype, ...] = dataclasses.field(
        default_factory=tuple
    )
    inputs: typing.Dict[str, str] = dataclasses.field(default_factory=dict)
    outputs: typing.Dict[str, str] = dataclasses.field(default_factory=dict)

    icon: str = "fa5s.toolbox"
