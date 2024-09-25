"""
Drag from ports to edges to make connections.
Edit edges by dragging them (not their ports)

Shift-Drag nodegraph to duplicate them.
Ctrl-Drag connections to add corners.

Middle Drag background to pan view.

"""

import os
from PySide6 import QtWidgets, QtGui
from radium.nodegraph import NodeGraphView
from radium.nodegraph import NodeGraphController
from radium.nodegraph import NodePrototype, PortPrototype

os.environ["QT_SCALE_FACTOR"] = "2"

app = QtWidgets.QApplication([])
view = NodeGraphView()

controller = NodeGraphController()
controller.attachView(view)

main_window = QtWidgets.QMainWindow()
main_window.setCentralWidget(view)

edit_menu = main_window.menuBar().addMenu("&Edit")

undo_action = controller.undo_stack.createUndoAction(edit_menu)
undo_action.setShortcut("Ctrl+Z")
edit_menu.addAction(undo_action)

redo_action = controller.undo_stack.createRedoAction(edit_menu)
redo_action.setShortcut("Ctrl+Y")
edit_menu.addAction(redo_action)


def delete_selection():
    selection = controller.selectedNodes()
    if not selection:
        return

    controller.undo_stack.beginMacro("Delete Selection")
    for node in selection:
        controller.removeItem(node)

    controller.undo_stack.endMacro()


delete_action = QtGui.QAction("&Delete", edit_menu)
delete_action.setShortcut("Delete")
delete_action.triggered.connect(delete_selection)
edit_menu.addAction(delete_action)

main_window.show()

merge_prototype = NodePrototype(
    "Merge",
    inputs=(PortPrototype("input1", "image"), PortPrototype("input2", "image")),
    outputs=(PortPrototype("output", "image"),),
    parameters=tuple(),
)
constant_prototype = NodePrototype(
    "Constant",
    inputs=tuple(),
    outputs=(PortPrototype("output", "image"),),
    parameters=tuple(),
)

controller.registerPrototype(merge_prototype)
controller.registerPrototype(constant_prototype)

app.exec()
