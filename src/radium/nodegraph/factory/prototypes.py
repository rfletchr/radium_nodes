__all__ = ["ParameterPrototype", "NodeType", "PortType"]
import typing
import dataclasses

RGBA = typing.Tuple[int, ...]


@dataclasses.dataclass(frozen=True)
class ParameterPrototype:
    name: str
    value: typing.Any
    datatype: str
    default: typing.Any = None
    metadata: typing.Dict[str, typing.Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True)
class PortType:
    type_name: str
    color: RGBA
    outline_color: RGBA


@dataclasses.dataclass(frozen=True)
class NodeType:
    name: str
    category: str

    color: RGBA = (64, 64, 64, 255)
    outline_color: RGBA = (32, 32, 32, 255)

    @property
    def type_name(self) -> str:
        return f"{self.category}/{self.name}"

    parameters: typing.Dict[str, ParameterPrototype] = dataclasses.field(
        default_factory=dict
    )

    inputs: typing.Dict[str, str] = dataclasses.field(default_factory=dict)
    outputs: typing.Dict[str, str] = dataclasses.field(default_factory=dict)

    icon: str = "fa5s.toolbox"
