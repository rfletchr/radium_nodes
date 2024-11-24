from PySide6 import QtCore, QtGui, QtWidgets
from radium.nodegraph.graph.scene.element import SerializableBaseElement


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


class Backdrop(SerializableBaseElement):
    def __init__(self, factory, node_type, name=None, parent=None):
        super().__init__(factory, type_name=node_type, name=name, parent=parent)
        self._name = name or node_type
        self.corner_a = BackdropHandle(parent=self)
        self.corner_b = BackdropHandle(parent=self)
        self.corner_b.setPos(100, 100)
        self.corner_a.setPos(-100, -100)

        self.setZValue(-5)

        self.__font = QtGui.QFont("Consolas", 10)
        self.__font_metrics = QtGui.QFontMetrics(self.__font)

    def paint(self, painter, option, widget=...):
        painter.setBrush(self.brush())
        painter.setPen(self.pen())
        painter.drawRoundedRect(self.boundingRect(), 6, 6)

        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 2))
        painter.setFont(self.__font)
        painter.setPen(QtCore.Qt.PenStyle.SolidLine)
        painter.drawText(
            self.boundingRect(), self._name, QtCore.Qt.AlignmentFlag.AlignHCenter
        )

    def boundingRect(self):
        return self.childrenBoundingRect()
