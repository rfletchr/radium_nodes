from PySide6 import QtCore, QtGui


def draw_grid(painter, rect, grid_size):
    """
    Draw a grid in the given rect with the given grid size.
    """
    grid_lines = []

    left = int(rect.left()) - (int(rect.left()) % grid_size)
    top = int(rect.top()) - (int(rect.top()) % grid_size)

    x = left
    while x < rect.right():
        grid_lines.append(QtCore.QLineF(x, rect.top(), x, rect.bottom()))
        x += grid_size

    y = top
    while y < rect.bottom():
        grid_lines.append(QtCore.QLineF(rect.left(), y, rect.right(), y))
        y += grid_size

    painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 25)))
    painter.drawLines(grid_lines)

    # draw x and y axis
    painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 72)))
    painter.drawLine(0, rect.top(), 0, rect.bottom())
    painter.drawLine(rect.left(), 0, rect.right(), 0)
