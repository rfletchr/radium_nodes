"""
A GraphicsItem that represents a node in a node nodegraph.
"""

import typing
import uuid

from PySide6 import QtCore, QtGui, QtWidgets, QtSvg
from radium.nodegraph.scene.port import InputPort, OutputPort

if typing.TYPE_CHECKING:
    from radium.nodegraph.scene.prototypes import NodePrototype


class Node(QtWidgets.QGraphicsPathItem):
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
            instance.addInput(port.name, port.datatype)

        for port in node.outputs.values():
            instance.addOutput(port.name, port.datatype)

        return instance

    def __init__(self, label: str, unique_id=None, parent=None):
        super().__init__(parent)
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(self.GraphicsItemFlag.ItemSendsScenePositionChanges, True)

        self.inputs: typing.Dict[str, InputPort] = {}
        self.outputs: typing.Dict[str, OutputPort] = {}

        self.__unique_id = unique_id or uuid.uuid4().hex
        self.__label = label
        self._font = QtGui.QFont("Consolas", 10)
        self._font_metrics = QtGui.QFontMetrics(self._font)
        self._name_rect = QtCore.QRectF()

        self.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))
        self.setBrush(QtGui.QColor(60, 60, 60))
        self.palette = QtGui.QPalette()
        self.__dirty = False
        self.setName(label)

    def unique_id(self):
        return self.__unique_id

    def name(self):
        return self.__label

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

        path = self.path()

        color = self.palette.color(self.palette.ColorRole.Light)

        painter.fillPath(path, color)

        if self.isSelected():
            color_role = self.palette.ColorRole.Highlight
        else:
            color_role = self.palette.ColorRole.Dark

        pen = QtGui.QPen(self.palette.color(color_role), 2)
        painter.strokePath(path, pen)

        painter.setFont(self._font)
        painter.drawText(self._name_rect, self.__label)

    def layout(self):
        if not self.__dirty:
            return

        rect = self._name_rect.adjusted(-5, -5, 5, 5)
        rect.setHeight(rect.width())

        rect.setWidth(max(rect.width(), 100))
        rect.moveCenter(QtCore.QPointF(0, 0))

        path = QtGui.QPainterPath()

        path.addRect(rect)
        self.setPath(path)
        self.__layoutPorts(
            self.inputs.values(), rect.top(), QtCore.Qt.AlignmentFlag.AlignBottom
        )
        self.__layoutPorts(
            self.outputs.values(), rect.bottom(), QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.__dirty = False

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

            if alignment & QtCore.Qt.AlignmentFlag.AlignBottom:
                y -= port.boundingRect().height() * 0.5
            elif alignment & QtCore.Qt.AlignmentFlag.AlignTop:
                y += port.boundingRect().height() * 0.5

            port.setPos(x + port.boundingRect().width() * 0.5, y)
            x += port.boundingRect().width() + spacing

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
