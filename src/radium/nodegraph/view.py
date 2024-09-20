from PySide6 import QtCore, QtWidgets, QtGui, QtOpenGLWidgets
from radium.nodegraph import util


class NodeGraphView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setTransformationAnchor(self.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(self.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewport(QtOpenGLWidgets.QOpenGLWidget())

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        super().drawBackground(painter, rect)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(self.palette().brush(self.palette().ColorRole.Window))
        painter.drawRect(rect)
        # TODO: Theme Support
        util.draw_grid(painter, rect, 20)

    def installEventFilter(self, filterObj):
        if isinstance(filterObj, NodeGraphViewEventFilter):
            print(
                "WARNING: NodeGraphViewEventFilter should be installed"
                " on the views viewport, not the view"
            )

        super().installEventFilter(filterObj)


class NodeGraphViewEventFilter(QtCore.QObject):
    nodeMenuRequested = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._mouse_down_pos = None

    def eventFilter(self, viewport: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if event.type() == QtCore.QEvent.Type.Wheel:
            return self.mouseWheelEvent(viewport, event)

        if event.type() == QtCore.QEvent.Type.MouseMove:
            return self.mouseMoveEvent(viewport, event)

        elif event.type() == QtCore.QEvent.Type.MouseButtonPress:
            self._mouse_down_pos = event.position()
            return super().eventFilter(viewport, event)

        elif event.type() == QtCore.QEvent.Type.KeyPress:
            self._mouse_down_pos = None

        return super().eventFilter(viewport, event)

    def keyPressEvent(self, viewport, event: QtGui.QKeyEvent) -> bool:
        if event.key() == QtCore.Qt.Key.Tab:
            self.nodeMenuRequested.emit()
            return True

        return False

    def mouseWheelEvent(self, viewport, event: QtGui.QWheelEvent) -> bool:
        zoom = 1.1 if event.angleDelta().y() > 0 else 0.9
        viewport.parent().scale(zoom, zoom)
        return True

    def mouseMoveEvent(self, viewport, event: QtGui.QMouseEvent) -> bool:
        view = viewport.parent()
        if event.buttons() == QtCore.Qt.MouseButton.MiddleButton:
            delta = event.position() - self._mouse_down_pos
            self._mouse_down_pos = event.position()

            vertical_scroll_bar = view.verticalScrollBar()
            horizontal_scroll_bar = view.horizontalScrollBar()

            x = horizontal_scroll_bar.value() - int(delta.x())
            y = vertical_scroll_bar.value() - int(delta.y())

            horizontal_scroll_bar.setValue(x)
            vertical_scroll_bar.setValue(y)

            return True
        return False


if __name__ == "__main__":
    from radium.nodegraph.controller import NodeGraphSceneController
    from radium.nodegraph.node import Node

    app = QtWidgets.QApplication([])
    scene = QtWidgets.QGraphicsScene()
    controller = NodeGraphSceneController(scene)

    node = Node("ReadImage", [], ["image"])
    node.setPos(0, 0)
    scene.addItem(node)

    node2 = Node("ReadImage2", [], ["image"])
    node2.setPos(0, 0)
    scene.addItem(node2)

    node2 = Node("Merge", ["image1", "image2"], ["image"])
    node2.setPos(0, 100)
    scene.addItem(node2)
    scene.setSceneRect(-1000, -1000, 2000, 2000)

    view = NodeGraphView()
    event_filter = NodeGraphViewEventFilter()
    view.viewport().installEventFilter(event_filter)
    view.show()
    view.setScene(scene)
    app.exec()
