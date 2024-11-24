import typing
import uuid

from PySide6 import QtWidgets, QtGui, QtCore

if typing.TYPE_CHECKING:
    from radium.nodegraph.factory.factory import NodeFactory


class BaseElementData(typing.TypedDict):
    node_type: str
    name: str
    position: typing.Tuple[float, float]
    unique_id: str


class SerializableBaseElement(QtWidgets.QGraphicsItem):
    """
    This is the base class for all serializable graph elements.
    """

    def __init__(
        self,
        factory: "NodeFactory",
        type_name: str,
        name: str = None,
        parent=None,
    ):
        super().__init__(parent=parent)
        self.__unique_id = uuid.uuid4().hex
        self.__type_name = type_name
        self.__name = name or type_name
        self.__factory = factory
        self.__brush = QtGui.QBrush()
        self.__pen = QtGui.QPen()

    def uniqueId(self):
        return self.__unique_id

    def pen(self):
        return self.__pen

    def setPen(self, pen):
        self.__pen = pen
        self.update()

    def brush(self):
        return self.__brush

    def setBrush(self, brush):
        self.__brush = brush
        self.update()

    def name(self):
        return self.__name

    def setName(self, name):
        self.__name = name

    def typeName(self):
        return self.__type_name

    def toDict(self):
        return BaseElementData(
            node_type=self.__type_name,
            name=self.__name,
            position=(self.pos().x(), self.pos().y()),
            unique_id=self.__unique_id,
        )

    def fromDict(self, data: BaseElementData):
        self.__type_name = data["node_type"]
        self.__name = data["name"]
        self.__unique_id = data["unique_id"]
        self.setPos(QtCore.QPointF(data["position"][0], data["position"][1]))
