from PySide6 import QtCore, QtWidgets, QtGui, QtOpenGLWidgets
from radium.nodegraph.scene import util

from radium.nodegraph.view.event_filter import NodeGraphViewEventFilter


class NodeGraphView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setTransformationAnchor(self.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(self.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewport(QtOpenGLWidgets.QOpenGLWidget())
        self.viewport().installEventFilter(NodeGraphViewEventFilter(self))

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        super().drawBackground(painter, rect)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(self.palette().brush(self.palette().ColorRole.Window))
        painter.drawRect(rect)
        util.draw_grid(painter, rect, 20)

    def installEventFilter(self, filterObj):
        if isinstance(filterObj, NodeGraphViewEventFilter):
            print(
                "WARNING: NodeGraphViewEventFilter should be installed"
                " on the views viewport, not the view"
            )

        super().installEventFilter(filterObj)
