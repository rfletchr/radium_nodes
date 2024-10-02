import sys
import typing

from PySide6 import QtWidgets, QtGui, QtCore
from radium.nodegraph.parameters.parameter import Parameter
from radium.nodegraph.parameters.view import editors

if typing.TYPE_CHECKING:
    from radium.nodegraph.graph.scene.node import Node


class ParameterEditorView(QtWidgets.QWidget):
    editorValueChanged = QtCore.Signal(Parameter, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.search = QtWidgets.QLineEdit(self)
        self.search.setPlaceholderText("Search")

        self.__container_layout = QtWidgets.QVBoxLayout()

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.search)
        main_layout.addLayout(self.__container_layout)
        main_layout.addStretch(100)

        self.__node_id_to_param_container = {}
        self.__node_id_to_param_widget_pairs = {}

    def addNode(self, node: "Node"):
        container = QtWidgets.QGroupBox(node.name())
        container.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum
        )

        layout = QtWidgets.QVBoxLayout(container)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.__node_id_to_param_container[node.uniqueId()] = container

        param_pairs = self.__node_id_to_param_widget_pairs[node.uniqueId()] = []

        for name, parameter in node.parameters().items():
            widget_cls = editors.ParameterEditorBase.from_datatype(parameter.datatype())
            widget = widget_cls()
            widget.setup(parameter)

            widget.valueChanged.connect(
                lambda v, p=parameter: self.editorValueChanged.emit(p, v)
            )

            parameter.valueChanged.subscribe(widget.onParameterChanged)

            param_pairs.append((parameter, widget))
            layout.addWidget(widget)

        self.__container_layout.insertWidget(0, container)

    def removeNode(self, node: "Node"):
        if node.uniqueId() not in self.__node_id_to_param_container:
            return

        container = self.__node_id_to_param_container.pop(node.uniqueId())
        self.__container_layout.removeWidget(container)
        container.deleteLater()

        param_pairs = self.__node_id_to_param_widget_pairs[node.uniqueId()]
        for param, widget in param_pairs:
            param.valueChanged.unSubscribe(widget.onParameterChanged)


if __name__ == "__main__":
    app = QtWidgets.QApplication()

    parameters = [
        Parameter("name", "text", "larry", "larry"),
        Parameter("number", "int", 100, 0, minimum=-200, maximum=200),
    ]

    editor = ParameterEditorView()
    editor.addParameters(parameters)
    editor.show()
    app.exec()
