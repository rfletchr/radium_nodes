import typing

from PySide6 import QtCore, QtWidgets, QtGui, QtOpenGLWidgets
from radium.nodegraph.graph import util

from radium.nodegraph.graph.view.event_filter import (
    NavigationEventFilter,
    DragDropEventFilter,
)

from radium.nodegraph.graph.scene import NodeGraphScene


class NodeGraphView(QtWidgets.QGraphicsView):
    itemDoubleClicked = QtCore.Signal(QtWidgets.QGraphicsItem)
    createNodeRequested = QtCore.Signal(str, QtCore.QPointF)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setTransformationAnchor(self.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(self.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewport(QtOpenGLWidgets.QOpenGLWidget())

        self.navigation_event_filter = NavigationEventFilter()
        self.drag_drop_event_filter = DragDropEventFilter()
        self.drag_drop_event_filter.nodeTypeDropped.connect(self.onNodeTypeDropped)

        self.viewport().installEventFilter(self.navigation_event_filter)
        self.viewport().installEventFilter(self.drag_drop_event_filter)

        self.viewport().setAcceptDrops(True)

        self.__hovered_item = None
        self.__node_creation_pos = QtCore.QPointF(0, 0)

    def onNodeTypeDropped(self, node_type: str):
        cursor = QtGui.QCursor.pos()
        scene_pos = self.mapToScene(self.mapFromGlobal(cursor))
        self.createNodeRequested.emit(node_type, scene_pos)

    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)

        item = self.itemAt(event.pos())
        if item:
            self.itemDoubleClicked.emit(item)

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        """
        Fill in the background of the graph, and draw a grid.
        """
        super().drawBackground(painter, rect)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(self.palette().brush(self.palette().ColorRole.Dark))
        painter.drawRect(rect)
        util.draw_grid(painter, rect, 20)

    def installEventFilter(self, filterObj):
        if isinstance(filterObj, NavigationEventFilter):
            print(
                "WARNING: NodeGraphViewEventFilter should be installed"
                " on the views view, not the view"
            )

        super().installEventFilter(filterObj)
