import typing
from PySide6 import QtWidgets, QtCore

from radium.nodegraph.scene.connection import Connection
from radium.nodegraph.scene.port import Port


class NodeGraphScene(QtWidgets.QGraphicsScene):
    itemAdded = QtCore.Signal(QtWidgets.QGraphicsItem)
    itemRemoved = QtCore.Signal(QtWidgets.QGraphicsItem)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSceneRect(-10000, -10000, 20000, 20000)
        self.__port_to_connections: typing.Dict[Port, typing.List[Connection]] = {}

    def addItem(self, item):
        if isinstance(item, Connection):
            self.addConnection(item)
        else:
            super().addItem(item)
        self.itemAdded.emit(item)

    def removeItem(self, item):
        if isinstance(item, Connection):
            self.removeConnection(item)
        else:
            super().removeItem(item)

        self.itemRemoved.emit(item)

    def getConnections(self, port):
        return self.__port_to_connections.get(port, [])

    def addConnection(self, connection: Connection):
        if connection.scene() is self:
            return

        super().addItem(connection)

        self.__port_to_connections.setdefault(connection.input_port, []).append(
            connection
        )
        self.__port_to_connections.setdefault(connection.output_port, []).append(
            connection
        )
        return connection

    def removeConnection(self, connection: Connection):
        super().removeItem(connection)
        self.__port_to_connections[connection.input_port].remove(connection)
        self.__port_to_connections[connection.output_port].remove(connection)

    def updatePortConnections(self, port: Port):
        connections = {
            connection for connection in self.__port_to_connections.get(port, [])
        }

        for connection in connections:
            connection.updatePath()
