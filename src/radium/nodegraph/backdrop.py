"""
A work in progress node graph backdrop node.

# TODO: integrate with input system so selection / connections work while inside a backdrop.

"""

from PySide6 import QtCore, QtGui, QtWidgets


class BackdropHandle(QtWidgets.QGraphicsRectItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(self.GraphicsItemFlag.ItemSendsScenePositionChanges)
        self.setRect(-6, -6, 12, 12)
        self.setBrush(QtGui.QColor(127, 127, 127))
        self.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))

    def itemChange(self, change, value):
        self.parentItem().layout()
        return super().itemChange(change, value)


class Backdrop(QtWidgets.QGraphicsRectItem):
    def __init__(self, name, parent=None):
        super().__init__(parent=parent)
        self._name = name
        self.corner_a = BackdropHandle(parent=self)
        self.corner_b = BackdropHandle(parent=self)
        self.corner_b.setPos(100, 100)
        self.corner_a.setPos(-100, -100)

        self.setPen(QtCore.Qt.PenStyle.NoPen)
        self.setBrush(QtGui.QColor(127, 127, 127, 127))
        self.setZValue(-1000)

        self._font = QtGui.QFont("Consolas", 10)
        self._font_metrics = QtGui.QFontMetrics(self._font)

    def paint(self, painter, option, widget = ...):
        painter.setBrush(self.brush())
        painter.setPen(self.pen())
        painter.drawRect(self.rect())

        text_rect = QtCore.QRectF(self._font_metrics.boundingRect(self._name))
        text_rect.moveCenter(QtCore.QPointF(0, 0))
        text_rect.setY(self.rect().top() - text_rect.height() - 2)

        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))
        painter.setFont(self._font)
        painter.setPen(QtCore.Qt.PenStyle.SolidLine)
        painter.drawText(text_rect, self._name)


    def layout(self):
        if not hasattr(self, "corner_a") or not hasattr(self, "corner_b"):
            return

        rect = QtCore.QRectF()
        rect.setTopLeft(self.corner_a.scenePos())
        rect.setBottomRight(self.corner_b.scenePos())
        self.setRect(rect.normalized())
