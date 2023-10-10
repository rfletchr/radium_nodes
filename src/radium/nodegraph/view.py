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

        # TODO: make this a signal/slot relationship? e.g. scene.gridSizeChanged.connect(self.setGridSize)
        if hasattr(self.scene(), "gridSize"):
            grid_size = self.scene().gridSize()
        else:
            grid_size = 20

        util.draw_grid(painter, rect, grid_size)

    def installEventFilter(self, filterObj):
        if isinstance(filterObj, NodeGraphViewEventFilter):
            print(
                "WARNING: NodeGraphViewEventFilter should be installed on the views viewport, not the view"
            )

        super().installEventFilter(filterObj)


class NodeGraphViewEventFilter(QtCore.QObject):
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

        return super().eventFilter(viewport, event)

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
            horizontal_scroll_bar.setValue(horizontal_scroll_bar.value() - int(delta.x()))
            vertical_scroll_bar.setValue(vertical_scroll_bar.value() - int(delta.y()))

            return True
        else:
            return False


if __name__ == "__main__":
    from radium.nodegraph.scene import NodeGraphScene
    from radium.nodegraph.node import Node
    from radium.nodegraph.backdrop import Backdrop

    app = QtWidgets.QApplication([])
    scene = NodeGraphScene()

    node = Node("ReadImage", [], ["image"])
    node.setPos(0, 0)
    scene.addItem(node)

    node2 = Node("BlurImage", ["image"], ["image"])
    node2.setPos(0, 100)
    scene.addItem(node2)
    scene.setSceneRect(-1000, -1000, 2000, 2000)

    # backdrop = Backdrop("Backdrop")
    # scene.addItem(backdrop)

    view = NodeGraphView()
    event_filter = NodeGraphViewEventFilter()
    view.viewport().installEventFilter(event_filter)
    view.show()
    view.setScene(scene)
    app.exec()
