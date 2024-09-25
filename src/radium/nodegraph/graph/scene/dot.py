"""
A dot is a NoOp node that can be used to aid in the layout of a node nodegraph
by adding corners to nodegraph connections.
"""

from PySide6 import QtCore, QtGui, QtWidgets
from radium.nodegraph.graph.scene.port import InputPort, OutputPort


class DotInputPort(InputPort):
    """
    A custom input node used by dots. This has a larger hit area.
    """

    def __init__(self, name, parent=None):
        super().__init__(name, "*", parent=parent)
        self.setBrush(QtGui.QColor(127, 0, 0, 32))
        self.setPen(QtCore.Qt.PenStyle.NoPen)
        self.setRect(-10, -10, 20, 10)
        self.setZValue(-1)


class DotOutputPort(OutputPort):
    """
    A custom output node used by dots. This has a larger hit area.
    """

    def __init__(self, name, parent=None):
        super().__init__(name, "*", parent=parent)
        self.setBrush(QtGui.QColor(0, 0, 0, 32))
        self.setPen(QtCore.Qt.PenStyle.NoPen)
        self.setRect(-10, 0, 20, 10)
        self.setZValue(-1)


class Dot(QtWidgets.QGraphicsEllipseItem):
    """
    A Dot node is a NoOp node used for graph layout.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable)
        self.setRect(-6, -6, 12, 12)
        self.setBrush(QtGui.QColor(127, 127, 127))
        self.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))

        self.input = DotInputPort("input", self)
        self.output = DotOutputPort("output", self)
