import typing
from PySide6 import QtGui, QtCore

from radium.nodegraph.graph.scene.node import Node
from radium.nodegraph.graph.scene.node_base import NodeDataDict
from radium.nodegraph.graph.scene.scene import NodeGraphScene
from radium.nodegraph.graph.scene.util import get_unique_name

if typing.TYPE_CHECKING:
    from radium.nodegraph.factory import NodeFactory
    from radium.nodegraph.graph.scene.scene import SceneDataDict


class GroupDataDict(NodeDataDict):
    scene: "SceneDataDict"


class Group(Node):
    def __init__(
        self,
        factory: "NodeFactory",
        type_name: str,
        name: str,
        parent=None,
    ):
        super().__init__(factory, type_name, name=name, parent=parent)
        self.__scene = NodeGraphScene()

    def subScene(self):
        return self.__scene

    def addInput(self, name: str, port_type: str):
        if name not in self.__scene.inputs():
            group_input = self.factory().createNode("group_input")
            group_input.setName(name)
            group_input.addOutput(name, port_type)
            group_input.calculateLayout()

            rect = group_input.boundingRect()
            width = rect.width()
            height = rect.height()

            x = ((width + 10) * len(self.__scene.inputs())) + 10 - width * 0.5
            y = -height * 2

            group_input.setPos(x, y)
            self.__scene.addItem(group_input)

        return super().addInput(name, port_type)

    def addOutput(self, name: str, port_type: str):
        if name not in self.__scene.outputs():
            group_output = self.factory().createNode("group_output")
            group_output.setName(name)
            group_output.addInput(name, port_type)
            group_output.calculateLayout()

            rect = group_output.boundingRect()
            width = rect.width()
            height = rect.height()

            x = ((width + 10) * len(self.__scene.outputs())) + 10 - width * 0.5
            y = height * 2

            group_output.setPos(x, y)
            self.__scene.addItem(group_output)

        return super().addOutput(name, port_type)

    def getUniqueInputName(self, prefix: str) -> str:
        return get_unique_name(prefix, self.inputs().keys())

    def getUniqueOutputName(self, prefix: str) -> str:
        return get_unique_name(prefix, self.outputs().keys())

    def toDict(self):
        data = super().toDict()
        data["scene"] = self.__scene.toDict()
        return data

    def loadDict(self, data: GroupDataDict) -> None:
        self.__scene.loadDict(data["scene"], self.factory())
        super().loadDict(data)

    def clipPath(self):
        rect = self.baseBoundingRect()
        path = QtGui.QPainterPath()

        x0 = rect.left()
        x3 = rect.right()
        y0 = rect.top()
        y3 = rect.bottom()

        h = rect.height()
        offset = h * 0.2

        points = [
            QtCore.QPoint(x0 + offset, y0),
            QtCore.QPoint(x3 - offset, y0),
            QtCore.QPoint(x3, y0 + offset),
            QtCore.QPoint(x3, y3 - offset),
            QtCore.QPoint(x3 - offset, y3),
            QtCore.QPoint(x0 + offset, y3),
            QtCore.QPoint(x0, y3 - offset),
            QtCore.QPoint(x0, y0 + offset),
        ]
        path.moveTo(points[0])
        for point in points[1:]:
            path.lineTo(point)

        path.closeSubpath()

        return path
