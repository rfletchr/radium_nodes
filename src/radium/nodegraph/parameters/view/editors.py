import typing
import contextlib
from PySide6 import QtWidgets, QtGui, QtCore

from radium.nodegraph.parameters.parameter import Parameter


class ParameterEditorBase(QtWidgets.QWidget):
    valueChanged = QtCore.Signal(object)

    @classmethod
    def from_datatype(cls, datatype):
        for subclass in cls.__subclasses__():
            try:
                if subclass.datatype() == datatype:
                    return subclass
            except NotImplementedError:
                continue

    @contextlib.contextmanager
    def muteSignals(self):
        self.blockSignals(True)
        try:
            yield
        finally:
            self.blockSignals(False)

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent)
        QtWidgets.QHBoxLayout(self)
        self.__label = QtWidgets.QLabel()
        self.layout().addWidget(self.__label)

    @classmethod
    def datatype(cls) -> str:
        raise NotImplementedError

    def setValue(self, value):
        raise NotImplemented

    def value(self):
        raise NotImplemented

    def bind(self, parameter: Parameter):
        with self.muteSignals():
            self.__label.setText(parameter.name())
            self.setValue(parameter.value())
            self.valueChanged.connect(parameter.setValue)


class TextParameterEditor(ParameterEditorBase):
    valueChanged = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.editor = QtWidgets.QLineEdit()
        self.editor.textChanged.connect(lambda text: self.valueChanged.emit(text))

        self.layout().addWidget(self.editor)

    @classmethod
    def datatype(cls) -> str:
        return "text"

    def setValue(self, value):
        self.editor.setText(value)

    def value(self):
        return self.editor.text()


class MultilineTextParameterEditor(ParameterEditorBase):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.editor = QtWidgets.QTextEdit()
        self.editor.textChanged.connect(self.valueChanged)

    @classmethod
    def datatype(cls) -> str:
        return "multiline-text"

    def setValue(self, value):
        self.editor.setText(value)

    def value(self):
        return self.editor.toPlainText()


class IntegerParameterEditor(ParameterEditorBase):
    valueChanged = QtCore.Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.editor = QtWidgets.QSpinBox()
        self.editor.valueChanged.connect(self.valueChanged)
        self.layout().addWidget(self.editor)

    @classmethod
    def datatype(cls) -> str:
        return "int"

    def setValue(self, value):
        self.editor.setValue(value)

    def value(self):
        return int(self.editor.text())

    def bind(self, parameter: Parameter):
        super().bind(parameter)

        with self.muteSignals():
            metadata = parameter.metadata()

            minimum = metadata.get("minimum", min(0, parameter.value()))
            maximum = metadata.get("maximum", max(1000000000, parameter.value()))

            self.editor.setMinimum(minimum)
            self.editor.setMaximum(maximum)


class FloatParameterEditor(ParameterEditorBase):
    valueChanged = QtCore.Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor = QtWidgets.QDoubleSpinBox()
        self.editor.valueChanged.connect(self.valueChanged)
        self.layout().addWidget(self.editor)

    @classmethod
    def datatype(cls) -> str:
        return "float"

    def setValue(self, value):
        self.editor.setValue(value)

    def value(self):
        return float(self.editor.text())


class BooleanParameterEditor(ParameterEditorBase):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.editor = QtWidgets.QCheckBox()
        self.editor.stateChanged.connect(self.valueChanged)
        self.layout().addWidget(self.editor)

    @classmethod
    def datatype(cls) -> str:
        return "bool"

    def setValue(self, value: bool):
        self.editor.setChecked(value)

    def value(self):
        return self.editor.isChecked()


class ColorPreview(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__color = QtGui.QColor()
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

    def setColor(self, color):
        self.__color = color

    def color(self):
        return self.__color

    def sizeHint(self):
        return QtCore.QSize(64, 64)

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        try:
            painter.setBrush(self.__color)
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.drawRect(self.rect())
        finally:
            painter.end()


class RGBAParameterEditor(ParameterEditorBase):
    valueChanged = QtCore.Signal(tuple)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pick_button = QtWidgets.QPushButton("Pick")
        self.preview = ColorPreview()

        self.layout().addWidget(self.preview)
        self.layout().addWidget(self.pick_button)

        self.pick_button.clicked.connect(self.onPickClicked)

    def onPickClicked(self):
        color = QtWidgets.QColorDialog.getColor(initial=self.preview.color())
        if color and color.isValid():
            self.preview.setColor(color)
            self.valueChanged.emit(self.value())

    @classmethod
    def datatype(cls):
        return "RGBA"

    def setValue(self, value):
        self.preview.setColor(QtGui.QColor(*value))

    def value(self):
        return (
            self.preview.color().red(),
            self.preview.color().green(),
            self.preview.color().blue(),
            self.preview.color().alpha(),
        )
