"""
A GraphicsItem that represents a node in a node graph.
"""
import typing

from PySide6 import QtCore, QtGui, QtWidgets
from radium.nodegraph.port import InputPort, OutputPort


class Node(QtWidgets.QGraphicsPathItem):
    def __init__(self, name, input_names, output_names, parent=None):
        super().__init__(parent)
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable)
        self.inputs: typing.Dict[str, InputPort] = {}
        self.outputs: typing.Dict[str, OutputPort] = {}

        self._name = name
        self._font = QtGui.QFont("Consolas", 10)
        self._font_metrics = QtGui.QFontMetrics(self._font)
        self._name_rect = QtCore.QRectF()

        self.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))
        self.setBrush(QtGui.QColor(60, 60, 60))
        self.palette = QtGui.QPalette()

        for input_name in input_names:
            self.addInput(input_name)

        for output_name in output_names:
            self.addOutput(output_name)

        # This triggers a layout call.
        self.setName(name)

    def setName(self, value, layout=True):
        rect = QtCore.QRectF(self._font_metrics.boundingRect(value))

        self._name_rect.setWidth(rect.width())
        self._name_rect.setHeight(rect.height())
        self._name_rect.moveCenter(QtCore.QPointF(0, 0))

        self._name = value

        if layout:
            self.layout()

    def paint(
            self,
            painter: QtGui.QPainter,
            option: QtWidgets.QStyleOptionGraphicsItem,
            widget=None,
    ):
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
        painter.drawText(self._name_rect, self._name)

    def layout(self):

        rect = self._name_rect.adjusted(-5, -5, 5, 5)

        rect.setWidth(max(rect.width(), 100))
        rect.moveCenter(QtCore.QPointF(0, 0))

        path = QtGui.QPainterPath()

        path.addRect(rect)
        self.setPath(path)

        self.layoutPorts(self.inputs.values(), rect.top() - 5)
        self.layoutPorts(self.outputs.values(), rect.bottom() + 5)

    def layoutPorts(self, ports, y):
        spacing = 10
        port_width = 10
        half_width = ((port_width + spacing) * (len(ports) - 1)) / 2

        for i, port in enumerate(ports):
            x = (i * (port_width + spacing)) - half_width
            port.setPos(x, y)

    def addInput(self, name):
        port = InputPort(name, self)
        self.inputs[name] = port
        return port

    def addOutput(self, name):
        port = OutputPort(name, self)
        self.outputs[name] = port
        return port

    def delete(self):
        for port in self.inputs.values():
            for connection in port._connections:
                connection.delete()

        for port in self.outputs.values():
            for connection in port._connections:
                connection.delete()

        self.scene().removeItem(self)
