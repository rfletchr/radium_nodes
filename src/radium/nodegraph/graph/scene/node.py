"""
A GraphicsItem that represents a node in a node nodegraph.
"""

import typing
import uuid
import qtawesome
from PySide6 import QtCore, QtGui, QtWidgets

from radium.nodegraph.graph.scene.port import InputPort, OutputPort
from radium.nodegraph.parameters.parameter import Parameter

if typing.TYPE_CHECKING:
    from radium.nodegraph.graph.scene.port import PortDataDict
    from radium.nodegraph.parameters.parameter import ParameterDataDict
    from radium.nodegraph.factory.prototypes import NodeType
    from radium.nodegraph.factory.factory import NodeFactory


class NodeDataDict(typing.TypedDict):
    node_type: str
    name: str
    position: typing.Tuple[float, float]
    unique_id: str
    inputs: typing.Dict[str, "PortDataDict"]
    outputs: typing.Dict[str, "PortDataDict"]
    parameters: typing.Dict[str, "ParameterDataDict"]


class NodeBase(QtWidgets.QGraphicsItem):
    def __init__(self, name: str, parent: QtWidgets.QGraphicsItem = None):
        super().__init__(parent=parent)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.__name = name

        self.__edited = False
        self.__viewed = False

        self.__layout_required = True

        self.__bounding_rect = QtCore.QRectF()
        self.__edited_rect = QtCore.QRectF()
        self.__viewed_rect = QtCore.QRectF()
        self.__text_rect = QtCore.QRectF()

        self.__corner_radius = 6.0
        self.__min_width = 150.0
        self.__spacing = 10.0

        self.__palette = pal = QtGui.QPalette()

        self.__selection_margin = 5.0
        self.__selection_pen = QtGui.QPen(pal.color(pal.ColorRole.Highlight), 2.0)
        self.__selection_bounding_rect = QtCore.QRectF()

        self.__pen = QtGui.QPen(QtGui.QPen(QtGui.QColor(24, 24, 24, 255), 4))
        self.__brush = QtGui.QBrush(QtGui.QBrush(QtGui.QColor(64, 64, 64, 255)))

        self.__edited_brush = QtGui.QBrush(QtGui.QColor(255, 64, 64, 255))
        self.__viewed_brush = QtGui.QBrush(QtGui.QColor(64, 64, 255, 255))

        self.__font = QtGui.QFont()
        self.__font_metrics = QtGui.QFontMetrics(self.__font)

        self.__shape = QtGui.QPainterPath()

    def setFont(self, font: QtGui.QFont):
        self.__font = font
        self.__font_metrics = QtGui.QFontMetrics(self.__font)
        self.__layout_required = True
        self.update()

    def font(self):
        return self.__font

    def setPen(self, pen: QtGui.QPen):
        self.__pen = pen
        self.update()

    def pen(self):
        return self.__pen

    def setBrush(self, brush: QtGui.QBrush):
        self.__brush = brush
        self.update()

    def brush(self):
        return self.__brush

    def isEdited(self):
        return self.__edited

    def setEdited(self, edited: bool):
        self.__edited = edited
        self.update()

    def isViewed(self):
        return self.__viewed

    def setViewed(self, viewed: bool):
        self.__viewed = viewed
        self.update()

    def setSelected(self, selected: bool):
        super().setSelected(selected)
        self.update()

    def setName(self, label: str):
        self.__name = label
        self.__layout_required = True
        self.update()

    def name(self):
        return self.__name

    def boundingRect(self):
        if self.isEdited():
            return self.__selection_bounding_rect
        return self.__bounding_rect

    def nonSelectionBoundingRect(self):
        return self.__bounding_rect

    def shape(self):
        return self.__shape

    def minimumWidth(self):
        return self.__min_width

    def calculateLayout(self, force=False):
        if not self.__layout_required and not force:
            return

        self.__text_rect = self.__font_metrics.boundingRect(self.name())
        self.__text_rect.moveCenter(QtCore.QPoint(0, 0))

        edit_rect_side = self.__text_rect.height()

        width = max(
            self.minimumWidth(),
            self.__text_rect.width() + (edit_rect_side * 2) + (self.__spacing * 2),
        )

        self.__bounding_rect.setWidth(width)
        self.__bounding_rect.setHeight(self.__text_rect.height() * 2)
        self.__bounding_rect.moveCenter(QtCore.QPoint(0, 0))

        self.__selection_bounding_rect = self.__bounding_rect.adjusted(
            -self.__selection_margin,
            -self.__selection_margin,
            self.__selection_margin,
            self.__selection_margin,
        )

        self.__edited_rect = QtCore.QRectF(
            self.__bounding_rect.right() - edit_rect_side,
            self.__bounding_rect.top(),
            edit_rect_side,
            self.__bounding_rect.height(),
        )

        self.__viewed_rect = QtCore.QRectF(
            self.__bounding_rect.left(),
            self.__bounding_rect.top(),
            edit_rect_side,
            self.__bounding_rect.height(),
        )

        self.__shape.clear()
        self.__shape.addRect(self.__bounding_rect)
        self.__layout_required = False

    def paint(self, painter: QtGui.QPainter, option, widget=None):
        self.calculateLayout()

        # create a clipping rect for the node with round corners if the border radius is above 0
        if self.__corner_radius:
            path = QtGui.QPainterPath()
            path.addRoundedRect(
                self.__bounding_rect, self.__corner_radius, self.__corner_radius
            )
            painter.setClipPath(path)

        # draw the nodes background
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(self.__brush)
        painter.drawRect(self.__bounding_rect)

        if self.isEdited():
            painter.setBrush(self.__edited_brush)
            painter.drawRect(self.__edited_rect)

        if self.isViewed():
            painter.setBrush(self.__viewed_brush)
            painter.drawRect(self.__viewed_rect)

        painter.setPen(self.__palette.color(self.__palette.ColorRole.Text))
        painter.drawText(
            self.__text_rect, self.name(), QtCore.Qt.AlignmentFlag.AlignCenter
        )

        painter.setPen(self.__palette.color(self.__palette.ColorRole.Window))
        painter.drawLine(self.__edited_rect.topLeft(), self.__edited_rect.bottomLeft())
        painter.drawLine(
            self.__viewed_rect.topRight(), self.__viewed_rect.bottomRight()
        )

        painter.setClipping(False)
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)

        painter.setPen(self.__pen)
        painter.drawRoundedRect(
            self.__bounding_rect, self.__corner_radius, self.__corner_radius
        )

        if self.isSelected():
            painter.setPen(self.__selection_pen)
            painter.drawRoundedRect(
                self.boundingRect(),
                self.__corner_radius,
                self.__corner_radius,
            )


class Node(NodeBase):
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
        data["unique_id"] = uuid.uuid4().hex
        return factory.createNodeInstance(data)

    def toDict(self):
        return NodeDataDict(
            node_type=self.nodeType(),
            name=self.name(),
            position=(self.pos().x(), self.pos().y()),
            unique_id=self.uniqueId(),
            inputs={k: v.toDict() for k, v in self.inputs().items()},
            outputs={k: v.toDict() for k, v in self.outputs().items()},
            parameters={k: v.toDict() for k, v in self.parameters().items()},
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

        for parameter_name, parameter_data in data["parameters"].items():
            if self.hasParameter(parameter_name):
                parameter = self.parameters()[parameter_name]
                parameter.loadDict(parameter_data)
            else:
                self.addParameter(
                    parameter_name,
                    parameter_data["datatype"],
                    parameter_data["value"],
                    parameter_data["default"],
                    **parameter_data["metadata"],
                )

    def __init__(
        self,
        factory: "NodeFactory",
        type_name: str,
        name: str = None,
        unique_id=None,
        parent=None,
    ):
        super().__init__(name or type_name, parent=parent)
        self.__factory: "NodeFactory" = factory
        self.__inputs: typing.Dict[str, InputPort] = {}
        self.__outputs: typing.Dict[str, OutputPort] = {}
        self.__parameters: typing.Dict[str, Parameter] = {}

        self.__unique_id = unique_id or uuid.uuid4().hex
        self.__node_type = type_name

    def inputs(self):
        return self.__inputs.copy()

    def outputs(self):
        return self.__outputs.copy()

    def parameters(self):
        return self.__parameters.copy()

    def uniqueId(self):
        return self.__unique_id

    def nodeType(self):
        return self.__node_type

    def calculateLayout(self, force=False):
        super().calculateLayout(force=force)
        rect = self.nonSelectionBoundingRect()
        self.__layoutPorts(
            self.__inputs.values(), rect.top(), QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.__layoutPorts(
            self.__outputs.values(), rect.bottom(), QtCore.Qt.AlignmentFlag.AlignBottom
        )

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

        def callback(
            previous,
            current,
            i=instance,
        ):
            self.scene().parameterChanged(self, i, previous, current)

        instance.valueChanged.subscribe(callback)
        self.__parameters[name] = instance

    def setSelected(self, selected: bool):
        super().setSelected(selected)
        self.scene().nodeSelected.emit(self)

    def setEdited(self, edited: bool):
        super().setEdited(edited)
        self.scene().nodeEdited.emit(self)
