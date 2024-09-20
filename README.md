# Radium Nodes

A no frills, vertical node-graph editor for PySide6.
![img](img/nodes.png)

```python
"""
Drag from ports to edges to make connections.
Edit edges by dragging them (not their ports)

Shift-Drag nodes to duplicate them.
Ctrl-Drag connections to add corners.

Middle Drag background to pan view.

On Linux use XCB Qt Backend where possible. wayland and PySide are not 100% working yet.

e.g.
    export QT_QPA_PLATFORM=xcb python example.py

"""
from PySide6 import QtWidgets
from radium.nodegraph import NodeGraphView, NodeGraphViewEventFilter
from radium.nodegraph import NodeGraphSceneController
from radium.nodegraph import Node

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
```
