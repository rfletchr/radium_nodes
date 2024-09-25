__all__ = ["NodeFactory"]
from PySide6 import QtCore
from radium.nodegraph.node_types.prototypes import NodePrototype
from radium.nodegraph.node_types.model import NodePrototypeModel


class NodeFactory(QtCore.QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__prototypes = {}
        self.node_types_model = NodePrototypeModel()

    def register(self, prototype: NodePrototype, exists_ok=False):
        if prototype.node_type in self.__prototypes:
            if not exists_ok:
                raise ValueError(f"NodePrototype: {prototype} already registered")
            else:
                self.node_types_model.removePrototype(prototype.node_type)

        self.__prototypes[prototype.node_type] = prototype
        self.node_types_model.addPrototype(prototype)

    def get_prototype(self, name):
        return self.__prototypes[name]

