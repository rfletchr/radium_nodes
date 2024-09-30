"""
A GraphicsItem that represents a node in a node nodegraph.
"""

import typing
import uuid

from PySide6 import QtCore, QtGui, QtWidgets

from radium.nodegraph.graph.scene.port import InputPort, OutputPort
from radium.nodegraph.parameters.parameter import Parameter

if typing.TYPE_CHECKING:
    from radium.nodegraph.factory.prototypes import NodeType
    from radium.nodegraph.factory.factory import NodeFactory


class NodeDataDict(typing.TypedDict):
    node_type: str
    name: str
    position: typing.Tuple[float, float]
    unique_id: str
    inputs: typing.Dict[str, typing.Dict]
    outputs: typing.Dict[str, typing.Dict]


class Node(QtWidgets.QGraphicsRectItem):
    @classmethod
    def fromPrototype(
        cls, node_type: "NodeType", factory: "NodeFactory", **kwargs
    ) -> "Node":
        kwargs.setdefault("name", node_type.name)
        node = cls(factory, node_type.type_name, **kwargs)

        for name, port_type in node_type.inputs.items():
            node.addInput(name, port_type)

        for name, port_type in node_type.outputs.items():
            node.addOutput(name, port_type)

        for name, param_data in node_type.parameters.items():
            node.addParameter(
                name,
                param_data.datatype,
                param_data.value,
                param_data.default,
                **param_data.metadata,
            )

        return node

    @classmethod
    def cloneNode(cls, node: "Node", factory: "NodeFactory") -> "Node":
        data = node.toDict()
        return factory.createNodeInstance(data)

    def toDict(self):
        return NodeDataDict(
            node_type=self.__node_type,
            name=self.__name,
            position=(self.pos().x(), self.pos().y()),
            unique_id=self.__unique_id,
            inputs={k: v.toDict() for k, v in self.inputs().items()},
            outputs={k: v.toDict() for k, v in self.outputs().items()},
        )

    def loadDict(self, data: NodeDataDict) -> None:
        self.__node_type = data["node_type"]
        self.__name = data["name"]
        self.setPos(QtCore.QPointF(data["position"][0], data["position"][1]))
        self.__unique_id = data["unique_id"]

        for port_name, port_data in data["inputs"].items():
            if self.hasInput(port_name):
                continue
            self.addInput(port_name, port_data["datatype"])

        for port_name, port_data in data["outputs"].items():
            if self.hasOutput(port_name):
                continue

            self.addOutput(port_name, port_data["datatype"])

    def __init__(
        self,
        factory: "NodeFactory",
        type_name: str,
        name: str = None,
        unique_id=None,
        parent=None,
    ):
        super().__init__(parent)
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(self.GraphicsItemFlag.ItemSendsScenePositionChanges, True)

        self.__factory: "NodeFactory" = factory
        self.__inputs: typing.Dict[str, InputPort] = {}
        self.__outputs: typing.Dict[str, OutputPort] = {}
        self.__parameters: typing.Dict[str, Parameter] = {}

        self.__unique_id = unique_id or uuid.uuid4().hex
        self.__node_type = type_name
        self.__name = name or type_name

        self._font = QtGui.QFont("Consolas", 10)
        self._font_metrics = QtGui.QFontMetrics(self._font)
        self._name_rect = QtCore.QRectF()

        self.palette = QtGui.QPalette()

        self.__dirty = False
        self.__rect = QtCore.QRectF()
        self.setName(self.__name)

    def inputs(self):
        return self.__inputs.copy()

    def outputs(self):
        return self.__outputs.copy()

    def parameters(self):
        return self.__parameters.copy()

    def uniqueId(self):
        return self.__unique_id

    def name(self):
        return self.__name

    def nodeType(self):
        return self.__node_type

    def setName(self, value, layout=True):
        rect = QtCore.QRectF(self._font_metrics.boundingRect(value))

        self._name_rect.setWidth(rect.width())
        self._name_rect.setHeight(rect.height())
        self._name_rect.moveCenter(QtCore.QPointF(0, 0))

        self.__name = value
        self.__dirty = True

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionGraphicsItem,
        widget=None,
    ):
        self.layout()

        painter.setBrush(self.brush())
        painter.drawRoundedRect(self.boundingRect(), 4, 4)

        if self.isSelected():
            color_role = self.palette.ColorRole.Highlight
            painter.setPen(QtGui.QPen(self.palette.color(color_role), 2))
        else:
            painter.setPen(self.pen())

        painter.drawRoundedRect(self.boundingRect(), 4, 4)

        pen = self.palette.color(self.palette.ColorRole.Text)
        painter.setPen(pen)
        painter.setFont(self._font)
        painter.drawText(self._name_rect, self.__name)

    def layout(self):
        if not self.__dirty:
            return

        rect = QtCore.QRectF()
        rect.setHeight(self._name_rect.height() * 1.5)
        rect.setWidth(max(100.0, self._name_rect.width() * 1.1))
        rect.moveCenter(QtCore.QPointF(0, 0))

        self.__rect = rect

        self.__layoutPorts(
            self.__inputs.values(), rect.top(), QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.__layoutPorts(
            self.__outputs.values(), rect.bottom(), QtCore.Qt.AlignmentFlag.AlignBottom
        )
        self.__dirty = False

    def boundingRect(self):
        return QtCore.QRectF(self.__rect)

    def shape(self):
        path = QtGui.QPainterPath()
        path.addRect(self.__rect)
        return path

    @staticmethod
    def __layoutPorts(
        ports,
        start_y,
        alignment: QtCore.Qt.AlignmentFlag,
        spacing=10,
        v_offset=2,
    ):
        ports = list(ports)
        width = sum(p.boundingRect().width() + spacing for p in ports) - spacing

        x = -width * 0.5

        for port in ports:
            y = start_y
            if alignment & QtCore.Qt.AlignmentFlag.AlignTop:
                y -= (port.boundingRect().height() * 0.5) + v_offset
            elif alignment & QtCore.Qt.AlignmentFlag.AlignBottom:
                y += (port.boundingRect().height() * 0.5) + v_offset

            port.setPos(x + port.boundingRect().width() * 0.5, y)
            x += port.boundingRect().width() + spacing

    def hasInput(self, name):
        return name in self.__inputs

    def hasOutput(self, name):
        return name in self.__outputs

    def addInput(self, name: str, datatype: str):
        if self.hasInput(name):
            raise ValueError(f"input: {name} already exists")

        port = self.__factory.createPortInstance(name, datatype, True)
        self.__inputs[name] = port
        port.setParentItem(self)

    def addOutput(self, name: str, datatype: str):
        if self.hasOutput(name):
            raise ValueError(f"output: {name} already exists")

        port = self.__factory.createPortInstance(name, datatype, False)
        self.__outputs[name] = port
        port.setParentItem(self)

    def hasParameter(self, name):
        return name in self.__parameters

    def addParameter(self, name, datatype, value, default, **kwargs):
        instance = Parameter(name, datatype, value, default, **kwargs)

        # instance.valueChanged.subscribe(
        #     lambda param, previous, value: self.scene().parameterChanged.emit(
        #         self, param, previous, value
        #     )
        # )

        self.__parameters[name] = instance
