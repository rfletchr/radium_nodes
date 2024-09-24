__all__ = ["ParameterPrototype", "PortPrototype", "NodePrototype"]
import typing
import dataclasses


@dataclasses.dataclass(frozen=True)
class ParameterPrototype:
    name: str
    default: typing.Any


@dataclasses.dataclass(frozen=True)
class PortPrototype:
    name: str
    datatype: str


@dataclasses.dataclass(frozen=True)
class NodePrototype:
    node_type: str
    parameters: typing.Tuple[ParameterPrototype, ...] = dataclasses.field(
        default_factory=tuple
    )
    inputs: typing.Tuple[PortPrototype, ...] = dataclasses.field(default_factory=tuple)
    outputs: typing.Tuple[PortPrototype, ...] = dataclasses.field(default_factory=tuple)
    icon: str = "fa5s.toolbox"

    def category(self):
        if "/" in self.node_type:
            return self.node_type[: self.node_type.rindex("/")]
        return "Nodes"

    def name(self):
        if "/" in self.node_type:
            return self.node_type[self.node_type.rindex("/") + 1 :]

        return self.node_type
