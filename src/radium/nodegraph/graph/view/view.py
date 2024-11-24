import typing
import logging

from PySide6 import QtCore, QtWidgets, QtGui, QtOpenGLWidgets

from radium.nodegraph.graph import util

from radium.nodegraph.graph.view.event_filter import (
    NavigationEventFilter,
    DragDropEventFilter,
)

from radium.nodegraph.graph.scene import NodeGraphScene

logger = logging.getLogger(__name__)


class NodeGraphView(QtWidgets.QWidget):
    itemDoubleClicked = QtCore.Signal(QtWidgets.QGraphicsItem)
    createNodeRequested = QtCore.Signal(str, QtCore.QPointF)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.viewer = NodeGraphViewport()
        self.top_text = QtWidgets.QLineEdit()
        self.top_text.setReadOnly(True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.top_text)
        layout.addWidget(self.viewer)

        self.viewer.itemDoubleClicked.connect(self.itemDoubleClicked)
        self.viewer.createNodeRequested.connect(self.createNodeRequested)

    def setScene(self, scene: NodeGraphScene):
        self.viewer.setScene(scene)

    def setHudText(self, text: str):
        self.top_text.setText(text)


class NodeGraphViewport(QtWidgets.QGraphicsView):
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
        self.__hud_text = ""

    def setHudText(self, text):
        self.__hud_text = text
        self.update()

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
            logger.warning(
                "WARNING: NodeGraphViewEventFilter should be installed"
                " on the views view, not the view"
            )

        super().installEventFilter(filterObj)
