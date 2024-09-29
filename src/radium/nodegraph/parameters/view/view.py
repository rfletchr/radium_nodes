import sys

from PySide6 import QtWidgets, QtGui, QtCore
from radium.nodegraph.parameters.parameter import Parameter
from radium.nodegraph.parameters.view import editors


class ParameterEditorView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search = QtWidgets.QLineEdit(self)
        self.search.setPlaceholderText("Search")

        self.list_widget = QtWidgets.QListWidget()

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.search)
        layout.addWidget(self.list_widget)

    def addParameters(self, parameters):
        for parameter in parameters:
            editor_cls = editors.ParameterEditorBase.from_datatype(parameter.datatype())

            if editor_cls is None:
                print("no widget for parameter", parameter)
                continue

            editor = editor_cls()

            editor.bind(parameter)
            editor.layout()

            item = QtWidgets.QListWidgetItem()
            item.setSizeHint(editor.sizeHint())

            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, editor)

    def clear(self):
        self.list_widget.clear()


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
