"""
A GraphicsItem that represents a connection between two ports.
"""
import typing

from PySide6 import QtGui, QtWidgets

if typing.TYPE_CHECKING:
    from radium.nodegraph.port import InputPort, OutputPort


class Connection(QtWidgets.QGraphicsPathItem):
    def __init__(self, input_port, output_port, parent=None):
        super().__init__(parent)
        self.setFlag(self.GraphicsItemFlag.ItemNegativeZStacksBehindParent)
        self.setZValue(-2)
        self.input_port: "InputPort" = input_port
        self.output_port: "OutputPort" = output_port

        self.input_port.disconnectAll()
        self.input_port.registerConnection(self)
        self.output_port.registerConnection(self)

        self.setPen(QtGui.QPen(QtGui.QColor(10, 10, 10, 200), 6))
        self.layout()

    def layout(self):
        path = QtGui.QPainterPath()

        path.moveTo(self.input_port.scenePos())
        path.lineTo(self.output_port.scenePos())

        self.setPath(path)

    def delete(self):
        self.input_port.unRegisterConnection(self)
        self.output_port.unRegisterConnection(self)
        if self.scene():
            self.scene().removeItem(self)
