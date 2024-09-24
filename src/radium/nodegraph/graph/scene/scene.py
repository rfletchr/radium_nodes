import typing
from PySide6 import QtWidgets, QtCore

from radium.nodegraph.graph.scene.connection import Connection
from radium.nodegraph.graph.scene.port import Port
from radium.nodegraph.graph.scene.node import Node


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

    def nodes(self):
        return [n for n in self.items() if isinstance(n, Node)]

    def selectedNodes(self):
        return [n for n in self.selectedItems() if isinstance(n, Node)]

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

    def dumpNodes(self, node_list: typing.List[Node]):
        result = {}
        nodes = result["nodes"] = {}
        connections = result["connections"] = []

        found_connections: typing.Set[Connection] = set()

        for node in node_list:
            nodes[node.uniqueId()] = node.toDict()
            for port in node.inputs():
                found_connections.update(self.getConnections(port))
            for port in node.outputs():
                found_connections.update(self.getConnections(port))

        for connection in found_connections:
            connections.append(connection.toDict())

        return result

    def dumpDict(self):
        nodes = [i for i in self.items() if isinstance(i, Node)]
        return self.dumpNodes(nodes)

    def loadDict(self, data):
        nodes = {}
        for node_id, node_data in data["nodes"].items():
            node = nodes[node_id] = Node.fromDict(node_data)
            self.addItem(node)

        for connection_data in data["connections"]:
            connection = Connection.fromDict(connection_data, nodes)
            self.addConnection(connection)
