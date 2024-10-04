__all__ = ["NodeBase", "NodeDataDict"]
MIN_NODE_WIDTH = 150.0
"""
This module contains the base class for implementing nodes. The logic is split into a number of 'private' base classes
to break down the class a little.
"""

import typing
import uuid
import logging

from PySide6 import QtCore, QtGui, QtWidgets

from radium.nodegraph.graph.scene.port import InputPort, OutputPort
from radium.nodegraph.parameters.parameter import Parameter

if typing.TYPE_CHECKING:
    from radium.nodegraph.graph.scene.port import PortDataDict
    from radium.nodegraph.parameters.parameter import ParameterDataDict
    from radium.nodegraph.factory.factory import NodeFactory

logger = logging.getLogger(__name__)


class NodeDataDict(typing.TypedDict):
    node_type: str
    name: str
    position: typing.Tuple[float, float]
    unique_id: str
    inputs: typing.Dict[str, "PortDataDict"]
    outputs: typing.Dict[str, "PortDataDict"]
    parameters: typing.Dict[str, "ParameterDataDict"]


class _NodeBase(QtWidgets.QGraphicsItem):
    def __init__(
        self,
        factory: "NodeFactory",
        type_name: str,
        name: str = None,
        parent: QtWidgets.QGraphicsItem = None,
    ):
        super().__init__(parent=parent)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)

        self.__name = name or type_name
        self.__node_type = type_name
        self.__unique_id = uuid.uuid4().hex
        self.__edited = False
        self.__viewed = False
        self.__factory = factory

        self.__parameters: typing.Dict[str, Parameter] = {}

    def factory(self):
        return self.__factory

    def nodeType(self):
        return self.__node_type

    def uniqueId(self):
        return self.__unique_id

    def inputs(self) -> typing.Dict[str, InputPort]:
        raise NotImplementedError

    def outputs(self) -> typing.Dict[str, OutputPort]:
        raise NotImplementedError

    def hasInput(self, name: str):
        raise NotImplementedError

    def hasOutput(self, name: str):
        raise NotImplementedError

    def addInput(self, name: str, port_type: str):
        raise NotImplementedError

    def addOutput(self, name: str, datatype: str):
        raise NotImplementedError

    def parameters(self) -> typing.Dict[str, "Parameter"]:
        return self.__parameters.copy()

    def parameter(self, name: str):
        return self.__parameters.get(name)

    def hasParameter(self, name: str):
        return name in self.__parameters

    def addParameter(self, name, datatype, value, default, **metadata):
        instance = self.__factory.createParameter(
            name, datatype, value, default, metadata
        )
        scene = self.scene()

        def callback(previous, current, i=instance, s=scene):
            s.parameterChanged(self, i, previous, current)

        instance.valueChanged.subscribe(callback)

        self.__parameters[name] = instance

    def isEdited(self):
        return self.__edited

    def setEdited(self, edited: bool):
        self.__edited = edited
        if hasattr(self.scene(), "nodeEdited"):
            self.scene().nodeEdited.emit(self)  # noqa

        self.update()

    def isViewed(self):
        return self.__viewed

    def setViewed(self, viewed: bool):
        self.__viewed = viewed
        self.update()

    def setSelected(self, selected: bool):
        super().setSelected(selected)
        if hasattr(self.scene(), "nodeSelected"):
            self.scene().nodeSelected.emit(self)  # noqa

        self.update()

    def setName(self, label: str):
        self.__name = label

    def name(self):
        return self.__name

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


class _DrawableNode(_NodeBase):
    """
    This class encapsulates the drawing logic for nodes.
    """

    def __init__(
        self,
        factory: "NodeFactory",
        type_name: str,
        name: str = None,
        parent: QtWidgets.QGraphicsItem = None,
    ):
        super().__init__(factory, type_name, name=name, parent=parent)

        self.__layout_required = True

        self.__bounding_rect = QtCore.QRectF()
        self.__edited_rect = QtCore.QRectF()
        self.__viewed_rect = QtCore.QRectF()
        self.__text_rect = QtCore.QRectF()

        self.__corner_radius = 6.0
        self.__min_width = 150.0
        self.__spacing = 10.0

        self.__palette = QtGui.QPalette()

        self.__pen = QtGui.QPen(QtGui.QPen(QtGui.QColor(24, 24, 24, 255), 4))
        self.__brush = QtGui.QBrush(QtGui.QBrush(QtGui.QColor(64, 64, 64, 255)))

        self.__edited_brush = QtGui.QBrush(QtGui.QColor(255, 64, 64, 255))
        self.__viewed_brush = QtGui.QBrush(QtGui.QColor(64, 64, 255, 255))

        self.__font = QtGui.QFont()
        self.__font_metrics = QtGui.QFontMetrics(self.__font)

    def cornerRadius(self):
        return self.__corner_radius

    def setCornerRadius(self, value):
        self.__corner_radius = value
        self.update()

    def palette(self):
        return self.__palette

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

    def boundingRect(self):
        return self.__bounding_rect

    def setName(self, name: str):
        super().setName(name)
        self.__layout_required = True
        self.update()

    def invalidateLayout(self):
        self.__layout_required = True

    def isLayoutValid(self):
        return not self.__layout_required

    def calculateLayout(self, force=False):
        if not self.__layout_required and not force:
            return

        # everything is driven by the nodes name. we first calculate the texts bounding rect and then use that to drive
        # the dimensions of the rest of the node.
        self.__text_rect = self.__font_metrics.boundingRect(self.name())
        self.__text_rect.moveCenter(QtCore.QPoint(0, 0))

        # calculate the w/h of of the left/right indicator boxes
        indicator_rect_side = self.__text_rect.height()

        # calculate the nodes total width accounting for a min width, text width and input/output ports
        inputs_width = calculate_total_width(self.inputs().values())
        outputs_width = calculate_total_width(self.outputs().values())

        width = max(
            MIN_NODE_WIDTH,
            self.__text_rect.width() + (indicator_rect_side * 2) + (self.__spacing * 2),
            inputs_width,
            outputs_width,
        )

        # calculate the bounding rect of the node.
        self.__bounding_rect.setWidth(width)
        self.__bounding_rect.setHeight(self.__text_rect.height() * 2)
        self.__bounding_rect.moveCenter(QtCore.QPoint(0, 0))

        # calculate the selection indicators rect.

        # calculate the edited/viewed indicators bounding boxes.
        self.__edited_rect = QtCore.QRectF(
            self.__bounding_rect.right() - indicator_rect_side,
            self.__bounding_rect.top(),
            indicator_rect_side,
            self.__bounding_rect.height(),
        )

        self.__viewed_rect = QtCore.QRectF(
            self.__bounding_rect.left(),
            self.__bounding_rect.top(),
            indicator_rect_side,
            self.__bounding_rect.height(),
        )

        # Layout Ports with inputs above the node, and outputs below.
        linear_layout(
            self.inputs().values(),
            self.__bounding_rect.top(),
            QtCore.Qt.AlignmentFlag.AlignTop,
            width=inputs_width,
        )

        linear_layout(
            self.outputs().values(),
            self.__bounding_rect.bottom(),
            QtCore.Qt.AlignmentFlag.AlignBottom,
            width=outputs_width,
        )

        self.__layout_required = False

    def paint(self, painter: QtGui.QPainter, option, widget=None):
        self.calculateLayout()

        lod = option.levelOfDetailFromTransform(painter.transform())

        # create a clipping rect for the node with round corners if the border radius is above 0
        if self.__corner_radius and lod > 0.5:
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

        if lod > 0.6:
            painter.setPen(self.__palette.color(self.__palette.ColorRole.Window))
            painter.drawLine(
                self.__edited_rect.topLeft(), self.__edited_rect.bottomLeft()
            )
            painter.drawLine(
                self.__viewed_rect.topRight(), self.__viewed_rect.bottomRight()
            )

        if lod > 0.3:
            painter.setOpacity(lod)
            painter.setPen(self.__palette.color(self.__palette.ColorRole.Text))
            painter.drawText(
                self.__text_rect, self.name(), QtCore.Qt.AlignmentFlag.AlignCenter
            )

        if lod > 0.4:
            painter.setClipping(False)
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)

            painter.setPen(self.__pen)
            painter.drawRoundedRect(
                self.__bounding_rect, self.__corner_radius, self.__corner_radius
            )


class _SelectableNode(_DrawableNode):
    """
    This class encapsulates any custom node selection painting/logic
    """

    def __init__(
        self,
        factory: "NodeFactory",
        type_name: str,
        name: str = None,
        parent: QtWidgets.QGraphicsItem = None,
    ):
        super().__init__(factory, type_name, name=name, parent=parent)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

        pal = self.palette()

        self.__selection_margin = 5.0
        self.__selection_pen = QtGui.QPen(
            pal.color(pal.ColorRole.Highlight), 2.0, QtCore.Qt.PenStyle.DotLine
        )
        self.__bounding_rect = QtCore.QRectF()
        self.__shape = QtGui.QPainterPath()

    def calculateLayout(self, force=False):
        if self.isLayoutValid():
            return
        super().calculateLayout(force=force)

        self.__bounding_rect = (
            super()
            .boundingRect()
            .adjusted(
                -self.__selection_margin,
                -self.__selection_margin,
                self.__selection_margin,
                self.__selection_margin,
            )
        )

        self.__shape.clear()
        self.__shape.addRect(super().boundingRect())

    def boundingRect(self):
        if self.isSelected():
            return self.__bounding_rect
        else:
            return super().boundingRect()

    def shape(self):
        return self.__shape

    def paint(self, painter: QtGui.QPainter, option, widget=None):
        super().paint(painter, option, widget)

        if self.isSelected():
            painter.setPen(self.__selection_pen)
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            painter.drawRect(self.boundingRect())


class NodeBase(_SelectableNode):
    """
    The base class used for nodes. Inherit from this class if you need to implement a custom node
    """


def calculate_total_width(items: typing.Iterable[QtWidgets.QGraphicsItem], spacing=10):
    """calculate the combined with for a collection of items accounting for spacing."""
    return sum(item.boundingRect().width() + spacing for item in items) - spacing


def linear_layout(
    items: typing.Iterable[QtWidgets.QGraphicsItem],
    start_y: float,
    alignment: QtCore.Qt.AlignmentFlag,
    spacing=10,
    v_offset=2,
    width: float = None,
):
    """
    Layout a collection of items in a line

    Args:
        items:
        start_y:
        alignment:
        spacing:
        v_offset:
        width:

    Returns:

    """

    if width is None:
        width = calculate_total_width(items, spacing)

    if width == 0:
        return

    x = -width * 0.5

    for port in items:
        y = start_y
        if alignment & QtCore.Qt.AlignmentFlag.AlignTop:
            y -= (port.boundingRect().height() * 0.5) + v_offset
        elif alignment & QtCore.Qt.AlignmentFlag.AlignBottom:
            y += (port.boundingRect().height() * 0.5) + v_offset

        port.setPos(x + port.boundingRect().width() * 0.5, y)
        x += port.boundingRect().width() + spacing
