"""
A GraphicsItem that represents a node in a node nodegraph.
"""

import json
import typing
import uuid

from PySide6 import QtCore, QtGui, QtWidgets

from radium.nodegraph.graph.scene.port import InputPort, OutputPort

if typing.TYPE_CHECKING:
    from radium.nodegraph.factory.prototypes import NodeType
    from radium.nodegraph.factory.factory import NodeFactory


class Node(QtWidgets.QGraphicsRectItem):
    @classmethod
    def fromPrototype(
        cls, node_type: "NodeType", factory: "NodeFactory", **kwargs
    ) -> "Node":
        kwargs.setdefault("name", node_type.name)
        node = cls(node_type.type_name, **kwargs)

        node.setPen(factory.createPen(node_type.outline_color))
        node.setBrush(factory.createBrush(node_type.color))

        for name, port_type in node_type.inputs.items():
            port = factory.createPortInstance(name, port_type, is_input=True)
            node.addPort(port)

        for name, port_type in node_type.outputs.items():
            port = factory.createPortInstance(name, port_type, is_input=False)
            node.addPort(port)

        return node

    @classmethod
    def fromNode(cls, node: "Node", factory: "NodeFactory") -> "Node":
        data = node.toDict()
        return cls.fromDict(data, factory)

    def toDict(self):
        return {
            "type": self.nodeType(),
            "name": self.name(),
            "position": [self.pos().x(), self.pos().y()],
            "unique_id": self.uniqueId(),
            "inputs": {k: v.toDict() for k, v in self.inputs().items()},
            "outputs": {k: v.toDict() for k, v in self.outputs().items()},
        }

    @classmethod
    def fromDict(cls, node_dict, factory: "NodeFactory"):

        if factory.hasNodeType(node_dict["type"]):
            instance = factory.createNodeInstance(
                node_dict["type"],
                unique_id=node_dict["unique_id"],
                name=node_dict["name"],
            )
        else:
            instance = cls(
                node_dict["type"],
                name=node_dict["name"],
                unique_id=node_dict["unique_id"],
            )
            instance.setBrush(factory.createBrush((127, 0, 0)))
            instance.setPen(factory.createPen((127, 0, 0)))

        pos = QtCore.QPointF(node_dict["position"][0], node_dict["position"][1])
        instance.setPos(pos)

        for name, input_data in node_dict["inputs"].items():
            if instance.hasPort(name, is_input=True):
                continue
            port = factory.createPortInstance(name, input_data, is_input=True)
            instance.addPort(port)

        for name, output_data in node_dict["outputs"].items():
            if instance.hasPort(name, is_input=False):
                continue
            port = factory.createPortInstance(name, output_data, is_input=False)
            instance.addPort(port)

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
        painter.drawText(self._name_rect, self.__label)

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

    def hasPort(self, name, is_input):
        store = self.__inputs if is_input else self.__outputs
        return name in store

    def addPort(self, port: typing.Union["InputPort", "OutputPort"]):
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
        port.setIndex(len(store))
        self.__dirty = True
