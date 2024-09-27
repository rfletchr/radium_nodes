__all__ = ["ParameterType", "NodeType", "PortType"]
import typing
import dataclasses

RGBA = typing.Tuple[int, int, int, int]


@dataclasses.dataclass(frozen=True)
class ParameterType:
    name: str
    default: typing.Any


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

    parameters: typing.Tuple[ParameterType, ...] = dataclasses.field(
        default_factory=tuple
    )

    inputs: typing.Dict[str, str] = dataclasses.field(default_factory=dict)
    outputs: typing.Dict[str, str] = dataclasses.field(default_factory=dict)

    icon: str = "fa5s.toolbox"
