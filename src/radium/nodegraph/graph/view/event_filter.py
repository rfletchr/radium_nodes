from PySide6 import QtCore, QtGui
from radium.nodegraph import constants


class DragDropEventFilter(QtCore.QObject):
    nodeTypeDropped = QtCore.Signal(str)

    def eventFilter(self, obj, event: QtCore.QEvent):
        if isinstance(event, QtGui.QDragEnterEvent):
            if event.mimeData().hasFormat(constants.NODE_TYPE_MIME_TYPE):
                event.accept()
                return True

        elif isinstance(event, QtGui.QDragMoveEvent):
            if event.mimeData().hasFormat(constants.NODE_TYPE_MIME_TYPE):
                event.accept()
                return True

        elif isinstance(event, QtGui.QDropEvent):
            if event.mimeData().hasFormat(constants.NODE_TYPE_MIME_TYPE):
                mime_data = event.mimeData()
                raw_data = mime_data.data(constants.NODE_TYPE_MIME_TYPE)
                self.nodeTypeDropped.emit(raw_data.toStdString())

        return False


class NavigationEventFilter(QtCore.QObject):
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

            x = horizontal_scroll_bar.value() - int(delta.x())
            y = vertical_scroll_bar.value() - int(delta.y())

            horizontal_scroll_bar.setValue(x)
            vertical_scroll_bar.setValue(y)

            return True
        return False
