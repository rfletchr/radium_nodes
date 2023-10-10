# Radium Nodes

A no frills, vertical node-graph editor for PySide6.
![img](img/nodes.png)

```python
from PySide6 import QtWidgets
from radium.nodegraph.view import NodeGraphView, NodeGraphViewEventFilter
from radium.nodegraph.scene import NodeGraphScene
from radium.nodegraph.node import Node

app = QtWidgets.QApplication([])
scene = NodeGraphScene()

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