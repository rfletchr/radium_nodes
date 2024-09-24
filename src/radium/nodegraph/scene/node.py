"""
A GraphicsItem that represents a node in a node nodegraph.
"""

import typing
import uuid

from PySide6 import QtCore, QtGui, QtWidgets, QtSvg
from radium.nodegraph.scene.port import InputPort, OutputPort, Port

if typing.TYPE_CHECKING:
    from radium.nodegraph.scene.prototypes import NodePrototype


class Node(QtWidgets.QGraphicsRectItem):
    @classmethod
    def from_prototype(cls, prototype: "NodePrototype"):
        node = cls(prototype.node_type)
        for port in prototype.inputs:
            node.addInput(port.name, port.datatype)

        for port in prototype.outputs:
            node.addOutput(port.name, port.datatype)

        return node

    @classmethod
    def from_node(cls, node: "Node") -> "Node":
        instance = cls(node.name())
        for port in node.inputs.values():
            instance.addInput(port.name(), port.datatype())

        for port in node.outputs.values():
            instance.addOutput(port.name(), port.datatype())

        return instance

    def toDict(self):
        return {
            "type": self.type(),
            "name": self.name(),
            "position": [self.pos().x(), self.pos().y()],
            "unique_id": self.unique_id(),
            "inputs": [i.toDict() for i in self.inputs.values()],
            "outputs": [o.toDict() for o in self.outputs.values()],
        }

    @classmethod
    def fromDict(cls, node_dict):
        instance = cls(node_dict["type"], name=node_dict["name"], unique_id=node_dict["unique_id"])

        pos = QtCore.QPointF(node_dict["position"][0], node_dict["position"][1])
        instance.setPos(pos)

        for input_data in node_dict["inputs"]:
            instance.addInput(input_data["name"], input_data["datatype"])

        for output_data in node_dict["outputs"]:
            instance.addOutput(output_data["name"], output_data["datatype"])

        return instance

    def __init__(self, type_name: str, name: str = None, unique_id=None, parent=None):
        super().__init__(parent)
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(self.GraphicsItemFlag.ItemSendsScenePositionChanges, True)

        self.inputs: typing.Dict[str, InputPort] = {}
        self.outputs: typing.Dict[str, OutputPort] = {}

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

    def unique_id(self):
        return self.__unique_id

    def name(self):
        return self.__label

    def type(self):
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
            self.inputs.values(), rect.top(), QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.__layoutPorts(
            self.outputs.values(), rect.bottom(), QtCore.Qt.AlignmentFlag.AlignBottom
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

    # TODO: make inputs/outputs functions and allow adding port instances.
    def addInput(self, name, datatype):
        port = InputPort(name, datatype, self)
        self.inputs[name] = port
        self.__dirty = True
        return port

    def addOutput(self, name, datatype):
        port = OutputPort(name, datatype, self)
        self.outputs[name] = port
        self.__dirty = True

        return port
