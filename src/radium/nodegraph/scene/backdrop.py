from PySide6 import QtCore, QtGui, QtWidgets


class BackdropHandle(QtWidgets.QGraphicsEllipseItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(self.GraphicsItemFlag.ItemSendsScenePositionChanges)
        self.setZValue(-4)
        self.setRect(-6, -6, 12, 12)
        self.setBrush(QtGui.QColor(127, 127, 127))
        self.setPen(QtCore.Qt.PenStyle.NoPen)

    def itemChange(self, change, value):
        self.parentItem().update()
        return super().itemChange(change, value)


class Backdrop(QtWidgets.QGraphicsItem):
    def __init__(self, name, parent=None):
        super().__init__(parent=parent)
        self._name = name
        self.corner_a = BackdropHandle(parent=self)
        self.corner_b = BackdropHandle(parent=self)
        self.corner_b.setPos(100, 100)
        self.corner_a.setPos(-100, -100)

        self.__pen = QtCore.Qt.PenStyle.NoPen
        self.__brush = QtGui.QColor(255, 127, 127, 64)
        self.setZValue(-5)

        self.__font = QtGui.QFont("Consolas", 10)
        self.__font_metrics = QtGui.QFontMetrics(self.__font)
        self.__rect = QtCore.QRectF()
        self.__text_rect = self.__font_metrics.boundingRect(self._name)

    def paint(self, painter, option, widget=...):
        painter.setBrush(self.__brush)
        painter.setPen(self.__pen)
        painter.drawRoundedRect(self.boundingRect(), 6, 6)

        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))
        painter.setFont(self.__font)
        painter.setPen(QtCore.Qt.PenStyle.SolidLine)
        painter.drawText(
            self.boundingRect(), self._name, QtCore.Qt.AlignmentFlag.AlignHCenter
        )

    def boundingRect(self):
        return self.childrenBoundingRect()
