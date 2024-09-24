"""
A GraphicsItem that represents a node in a node nodegraph.
"""

import typing
import uuid

from PySide6 import QtCore, QtGui, QtWidgets
from radium.nodegraph.graph.scene.port import InputPort, OutputPort

if typing.TYPE_CHECKING:
    from radium.nodegraph.graph.scene.prototypes import NodePrototype


class Node(QtWidgets.QGraphicsRectItem):
    @classmethod
    def fromPrototype(cls, prototype: "NodePrototype"):
        node = cls(prototype.node_type)
        for port_prototype in prototype.inputs:
            node.addPort(InputPort.fromPrototype(port_prototype))

        for port_prototype in prototype.outputs:
            node.addPort(OutputPort.fromPrototype(port_prototype))

        return node

    @classmethod
    def fromNode(cls, node: "Node") -> "Node":
        data = node.toDict()
        return cls.fromDict(data)

    def toDict(self):
        return {
            "type": self.nodeType(),
            "name": self.name(),
            "position": [self.pos().x(), self.pos().y()],
            "unique_id": self.uniqueId(),
            "inputs": [i.toDict() for i in self.inputs().values()],
            "outputs": [o.toDict() for o in self.outputs().values()],
        }

    @classmethod
    def fromDict(cls, node_dict):
        instance = cls(
            node_dict["type"], name=node_dict["name"], unique_id=node_dict["unique_id"]
        )

        pos = QtCore.QPointF(node_dict["position"][0], node_dict["position"][1])
        instance.setPos(pos)

        for input_data in node_dict["inputs"]:
            instance.addPort(InputPort.fromDict(input_data))

        for output_data in node_dict["outputs"]:
            instance.addPort(OutputPort.fromDict(output_data))

        return instance

    def __init__(self, type_name: str, name: str = None, unique_id=None, parent=None):
        super().__init__(parent)
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(self.GraphicsItemFlag.ItemSendsScenePositionChanges, True)

        self.__inputs: typing.Dict[str, InputPort] = {}
        self.__outputs: typing.Dict[str, OutputPort] = {}

        self.__unique_id = unique_id or uuid.uuid4().hex
        self.__type = type_name
        self.__label = name or type_name
        self._font = QtGui.QFont("Consolas", 10)
        self._font_metrics = QtGui.QFontMetrics(self._font)
        self._name_rect = QtCore.QRectF()

        self.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))
        self.setBrush(QtGui.QColor(60, 60, 60))
        self.palette = QtGui.QPalette()
        self.__dirty = False
        self.__rect = QtCore.QRectF()
        self.setName(self.__label)

    def inputs(self):
        return self.__inputs.copy()

    def outputs(self):
        return self.__outputs.copy()

    def uniqueId(self):
        return self.__unique_id

    def name(self):
        return self.__label

    def nodeType(self):
        return self.__type

    def setName(self, value, layout=True):
        rect = QtCore.QRectF(self._font_metrics.boundingRect(value))

        self._name_rect.setWidth(rect.width())
        self._name_rect.setHeight(rect.height())
        self._name_rect.moveCenter(QtCore.QPointF(0, 0))

        self.__label = value
        self.__dirty = True

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionGraphicsItem,
        widget=None,
    ):
        self.layout()

        color = self.palette.color(self.palette.ColorRole.Light)
        painter.setBrush(color)
        painter.drawRoundedRect(self.boundingRect(), 10, 10)

        if self.isSelected():
            color_role = self.palette.ColorRole.Highlight
        else:
            color_role = self.palette.ColorRole.Dark

        pen = QtGui.QPen(self.palette.color(color_role), 2)
        painter.setPen(pen)
        painter.drawRoundedRect(self.boundingRect(), 10, 10)

        pen = self.palette.color(self.palette.ColorRole.Text)
        painter.setPen(pen)
        painter.setFont(self._font)
        painter.drawText(self._name_rect, self.__label)

    def layout(self):
        if not self.__dirty:
            return

        rect = self._name_rect.adjusted(-5, 0, 5, 0)
        rect.setHeight(rect.height() * 3)
        rect.setWidth(rect.width() * 1.5)

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
    ):
        ports = list(ports)
        width = sum(p.boundingRect().width() + spacing for p in ports) - spacing

        x = -width * 0.5

        for port in ports:
            y = start_y
            port.setPos(x + port.boundingRect().width() * 0.5, y)
            x += port.boundingRect().width() + spacing

    def addPort(self, port: typing.Union[InputPort, OutputPort]):
        if isinstance(port, InputPort):
            store = self.__inputs
        elif isinstance(port, OutputPort):
            store = self.__outputs
        else:
            raise TypeError(f"Unknown input/output port type: {port}")

        if port.name() in store:
            raise ValueError(f"Port {port.name()} already exists")

        store[port.name()] = port
        port.setParentItem(self)
        self.__dirty = True
