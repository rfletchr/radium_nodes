"""
A GraphicsItem that represents a connection between two ports.
"""

import typing

from PySide6 import QtGui, QtWidgets

if typing.TYPE_CHECKING:
    from radium.nodegraph.scene.port import InputPort, OutputPort


class Connection(QtWidgets.QGraphicsPathItem):
    def __init__(self, output_port, input_port, parent=None):
        super().__init__(parent)
        self.setZValue(-2)
        self.input_port: "InputPort" = input_port
        self.output_port: "OutputPort" = output_port
        self.setPen(QtGui.QPen(QtGui.QColor(24, 24, 24, 255), 6))
        self.updatePath()

    def paint(self, painter, option, widget=...):
        painter.setPen(self.pen())
        painter.drawEllipse(self.input_port.scenePos(), 6, 6)
        painter.drawEllipse(self.output_port.scenePos(), 6, 6)
        super().paint(painter, option, widget)

    def updatePath(self):
        path = QtGui.QPainterPath()

        x1 = self.output_port.scenePos().x()
        y1 = self.output_port.scenePos().y()

        x4 = self.input_port.scenePos().x()
        y4 = self.input_port.scenePos().y()

        dx = x4 - x1
        dy = y4 - y1

        path.moveTo(x1, y1)

        if abs(dx) > 5:
            x2 = x1
            y2 = y1 + (dy * 0.5)

            x3 = x4
            y3 = y1 + (dy * 0.5)

            path.lineTo(x2, y2)
            path.lineTo(x3, y3)
        else:
            x4 = x1

        path.lineTo(x4, y4)

        self.setPath(path)
