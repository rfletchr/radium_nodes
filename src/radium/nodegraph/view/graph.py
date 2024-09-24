from PySide6 import QtCore, QtWidgets, QtGui, QtOpenGLWidgets
from radium.nodegraph.scene import util

from radium.nodegraph.view.event_filter import NodeGraphViewEventFilter
from radium.nodegraph.view.node_list import NodeSearchBox


class NodeGraphView(QtWidgets.QGraphicsView):
    createNodeRequested = QtCore.Signal(QtCore.QModelIndex, QtCore.QPointF)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setTransformationAnchor(self.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(self.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewport(QtOpenGLWidgets.QOpenGLWidget())
        self.viewport().installEventFilter(NodeGraphViewEventFilter(self))
        self.search_box = NodeSearchBox()
        self.search_box.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.search_box.itemSelected.connect(self.onSearchBoxAccepted)

        tab_action = QtGui.QAction(self)
        tab_action.setShortcut(QtCore.Qt.Key.Key_Tab)
        tab_action.triggered.connect(self.onSearchBoxRequested)

        self.__node_creation_pos = QtCore.QPointF(0, 0)

        self.addAction(tab_action)

    def onSearchBoxRequested(self):
        self.__node_creation_pos = self.mapToScene(self.mapFromGlobal(QtGui.QCursor.pos()))
        self.search_box.show()

    def onSearchBoxAccepted(self, index: QtCore.QModelIndex) -> None:
        self.createNodeRequested.emit(index, self.__node_creation_pos)

    def setNodesModel(self, model: QtCore.QAbstractItemModel) -> None:
        self.search_box.setModel(model)

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
