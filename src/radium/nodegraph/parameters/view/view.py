import sys

from PySide6 import QtWidgets, QtGui, QtCore
from radium.nodegraph.parameters.parameter import Parameter
from radium.nodegraph.parameters.view import editors


class ParameterEditorView(QtWidgets.QWidget):
    editorValueChanged = QtCore.Signal(Parameter, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.search = QtWidgets.QLineEdit(self)
        self.search.setPlaceholderText("Search")

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setSelectionMode(self.list_widget.SelectionMode.NoSelection)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.search)
        layout.addWidget(self.list_widget)

        self.__subs = []

    def addParameters(self, parameters):
        for parameter in parameters:
            editor_cls = editors.ParameterEditorBase.from_datatype(parameter.datatype())

            if editor_cls is None:
                print("no widget for parameter", parameter)
                continue

            editor = editor_cls()
            editor.valueChanged.connect(
                lambda v, p=parameter: self.editorValueChanged.emit(p, v)
            )
            editor.setup(parameter)
            editor.layout()

            parameter.valueChanged.subscribe(editor.onParameterChanged)
            self.__subs.append((parameter, editor.onParameterChanged))

            item = QtWidgets.QListWidgetItem()
            item.setSizeHint(editor.sizeHint())

            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, editor)

    def clear(self):
        self.list_widget.clear()

        # pyside objects and weak refs don't play very nicely so unsubscribe
        for parameter, editor_func in self.__subs:
            parameter.valueChanged.unSubscribe(editor_func)

        self.__subs.clear()


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
