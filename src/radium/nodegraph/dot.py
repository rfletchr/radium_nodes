"""
A GraphicsItem that represents a dot. A dot is a NoOp node that can be used to aid in the layout of a node graph by
adding corners to graph connections.
"""
import copy
import typing

from PySide6 import QtCore, QtGui, QtWidgets
from radium.nodegraph.port import InputPort, OutputPort


class DotInputPort(InputPort):
    def __init__(self, name, parent=None):
        super().__init__(name, parent=parent)
        self.setBrush(QtGui.QColor(0, 0, 0, 32))
        self.setPen(QtCore.Qt.PenStyle.NoPen)
        path = QtGui.QPainterPath()
        path.addRect(-10, -10, 20, 10)
        self.setPath(path)


class DotOutputPort(OutputPort):
    def __init__(self, name, parent=None):
        super().__init__(name, parent=parent)
        self.setBrush(QtGui.QColor(0, 0, 0, 32))
        self.setPen(QtCore.Qt.PenStyle.NoPen)
        path = QtGui.QPainterPath()
        path.addRect(-10, 0, 20, 10)
        self.setPath(path)


class Dot(QtWidgets.QGraphicsEllipseItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable)
        self.setRect(-6, -6, 12, 12)
        self.setBrush(QtGui.QColor(127, 127, 127))
        self.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))

        self.input = DotInputPort("input", self)
        self.output = DotOutputPort("output", self)
