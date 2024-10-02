import os.path
import qtawesome as qta
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
        self.__mute_level += 1
        try:
            yield
        finally:
            self.__mute_level -= 1
            if self.__mute_level == 0:
                self.blockSignals(False)

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent)
        self.__mute_level = 0
        layout = QtWidgets.QHBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.__label = QtWidgets.QLabel()
        self.layout().addWidget(self.__label)

    @classmethod
    def datatype(cls) -> str:
        raise NotImplementedError

    def setValue(self, value):
        raise NotImplemented

    def value(self):
        raise NotImplemented

    def setup(self, parameter: Parameter):
        with self.muteSignals():
            self.__label.setText(parameter.name())
            self.setValue(parameter.value())

    def onParameterChanged(self, _, value):
        with self.muteSignals():
            self.setValue(value)


class TextParameterEditor(ParameterEditorBase):
    valueChanged = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.editor = QtWidgets.QLineEdit()
        self.editor.editingFinished.connect(self.onEditingFinished)
        self.layout().addWidget(self.editor)

    def onEditingFinished(self):
        # NOTE: clearing focus triggers another editing finished event.
        self.editor.blockSignals(True)
        self.editor.clearFocus()
        self.editor.blockSignals(False)

        value = self.editor.text()
        self.valueChanged.emit(value)

    @classmethod
    def datatype(cls) -> str:
        return "text"

    def setValue(self, value):
        self.editor.setText(value)

    def value(self):
        return self.editor.text()


class IntegerParameterEditor(ParameterEditorBase):
    valueChanged = QtCore.Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.editor = QtWidgets.QSpinBox()
        self.editor.editingFinished.connect(self.onEditingFinished)
        self.layout().addWidget(self.editor)
        self.__prev = None

    def onEditingFinished(self):
        # NOTE: clearing focus triggers another editing finished event.
        self.editor.blockSignals(True)
        self.editor.clearFocus()
        self.editor.blockSignals(False)

        value = self.editor.value()
        self.valueChanged.emit(value)

    @classmethod
    def datatype(cls) -> str:
        return "int"

    def setValue(self, value):
        with self.muteSignals():
            self.editor.setValue(value)
        self.valueChanged.emit(self.editor.value())

    def value(self):
        return int(self.editor.text())

    def setup(self, parameter: Parameter):
        with self.muteSignals():
            metadata = parameter.metadata()

            minimum = metadata.get("minimum", min(0, parameter.value()))
            maximum = metadata.get("maximum", max(1000000000, parameter.value()))

            self.editor.setMinimum(minimum)
            self.editor.setMaximum(maximum)

        super().setup(parameter)


class FloatParameterEditor(ParameterEditorBase):
    valueChanged = QtCore.Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor = QtWidgets.QDoubleSpinBox()
        self.editor.editingFinished.connect(self.onEditingFinished)
        self.layout().addWidget(self.editor)

    def onEditingFinished(self):
        # NOTE: clearing focus triggers another editing finished event.
        self.editor.blockSignals(True)
        self.editor.clearFocus()
        self.editor.blockSignals(False)

        value = self.editor.value()
        self.valueChanged.emit(value)

    @classmethod
    def datatype(cls) -> str:
        return "float"

    def setValue(self, value):
        with self.muteSignals():
            self.editor.setValue(value)
        self.valueChanged.emit(self.editor.value())

    def value(self):
        return float(self.editor.text())

    def setup(self, parameter: Parameter):
        with self.muteSignals():
            metadata = parameter.metadata()

            minimum = metadata.get("minimum", min(0, parameter.value()))
            maximum = metadata.get("maximum", max(1000000000, parameter.value()))

            self.editor.setMinimum(minimum)
            self.editor.setMaximum(maximum)

        super().setup(parameter)


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
        self.setMinimumWidth(64)
        self.setMinimumHeight(64)

    def setColor(self, color):
        self.__color = color
        self.update()

    def color(self):
        return self.__color

    def sizeHint(self):
        return QtCore.QSize(64, 64)

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        try:
            min_side = min(event.rect().width(), event.rect().height())
            rect = QtCore.QRect(0, 0, min_side, min_side)
            rect.moveCenter(event.rect().center())

            painter.setBrush(self.__color)
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect, 5, 5)
        finally:
            painter.end()


class IntSlider(QtWidgets.QWidget):
    valueChanged = QtCore.Signal(int)
    valueChanging = QtCore.Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.spinner = QtWidgets.QSpinBox()

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.slider)
        layout.addWidget(self.spinner)

        self.spinner.editingFinished.connect(self.onSpinnerEditingFinished)
        self.spinner.textChanged.connect(self.onSpinnerTextChanged)
        self.slider.sliderReleased.connect(self.onSliderReleased)

        self.slider.sliderMoved.connect(self.onSliderMoved)

    def onSpinnerTextChanged(self):
        self.blockSignals(True)
        self.slider.setValue(self.spinner.value())
        self.blockSignals(False)
        self.valueChanging.emit(self.spinner.value())

    def onSpinnerEditingFinished(self):
        self.blockSignals(True)
        self.slider.setValue(self.spinner.value())
        self.blockSignals(False)

        self.valueChanged.emit(self.spinner.value())

    def onSliderMoved(self, value):
        self.blockSignals(True)
        self.spinner.setValue(value)
        self.blockSignals(False)

        self.valueChanging.emit(value)

    def onSliderReleased(self):
        self.valueChanged.emit(self.slider.value())

    def setValue(self, value):
        self.blockSignals(True)
        self.slider.setValue(value)
        self.spinner.setValue(value)
        self.blockSignals(False)
        self.valueChanged.emit(value)

    def value(self):
        return self.slider.value()

    def setMinimum(self, minimum):
        self.spinner.setMinimum(minimum)
        self.slider.setMinimum(minimum)

    def setMaximum(self, maximum):
        self.spinner.setMaximum(maximum)
        self.slider.setMaximum(maximum)

    def setRange(self, minimum, maximum):
        self.setMinimum(minimum)
        self.setMaximum(maximum)


class RGBAParameterEditor(ParameterEditorBase):
    valueChanged = QtCore.Signal(tuple)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pick_button = QtWidgets.QPushButton()
        self.pick_button.setIcon(qta.icon("fa.eyedropper"))
        self.pick_button.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self.preview = ColorPreview()

        self.r_slider = IntSlider()
        self.g_slider = IntSlider()
        self.b_slider = IntSlider()
        self.a_slider = IntSlider()

        slider_layout = QtWidgets.QFormLayout()
        slider_layout.setContentsMargins(0, 0, 0, 0)

        for name, slider in [
            ("r", self.r_slider),
            ("g", self.g_slider),
            ("b", self.b_slider),
            ("a", self.a_slider),
        ]:
            slider.setMinimum(0)
            slider.setMaximum(255)
            if name == "a":
                slider.setValue(255)
            else:
                slider.setValue(127)
            slider_layout.addRow(name, slider)

            slider.valueChanged.connect(self.onSliderChanged)
            slider.valueChanging.connect(self.onSliderDragging)

        self.layout().addLayout(slider_layout)
        self.layout().addWidget(self.preview)
        self.layout().addWidget(self.pick_button)

        self.pick_button.clicked.connect(self.onPickClicked)

    def onSliderDragging(self, *_):
        preview_color = QtGui.QColor(
            self.r_slider.value(),
            self.g_slider.value(),
            self.b_slider.value(),
            self.a_slider.value(),
        )
        self.preview.setColor(preview_color)

    def onSliderChanged(self, *_):
        self.valueChanged.emit(self.value())

    def onPickClicked(self):
        color = QtWidgets.QColorDialog.getColor(initial=self.preview.color())
        if color and color.isValid():
            self.setValue((color.red(), color.green(), color.blue(), color.alpha()))

    @classmethod
    def datatype(cls):
        return "RGBA"

    def setValue(self, value):
        self.preview.setColor(QtGui.QColor(*value))
        with self.muteSignals():
            self.r_slider.setValue(value[0])
            self.g_slider.setValue(value[1])
            self.b_slider.setValue(value[2])
            self.a_slider.setValue(value[3])
        self.valueChanged.emit(value)

    def value(self):
        return (
            self.preview.color().red(),
            self.preview.color().green(),
            self.preview.color().blue(),
            self.preview.color().alpha(),
        )

    def setup(self, parameter: Parameter):
        with self.muteSignals():
            super().setup(parameter)


class FilenameEditor(ParameterEditorBase):
    valueChanged = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pick_button = QtWidgets.QPushButton()
        self.pick_button.setIcon(qta.icon("fa.folder"))
        self.path_edit = QtWidgets.QLineEdit()

        self.layout().addWidget(self.path_edit)
        self.layout().addWidget(self.pick_button)

        self.__filters = ""
        self.__dir = "~"
        self.__caption = "pick a file"
        self.__save_file = False
        self.path_edit.textChanged.connect(self.valueChanged)
        self.pick_button.clicked.connect(self.onPickClicked)

    def onPickClicked(self):
        if self.__save_file:
            path, _ = QtWidgets.QFileDialog.getSaveFileName(
                dir=os.path.expandvars(os.path.expanduser(self.__dir)),
                filter=self.__filters,
                caption=self.__caption,
            )
        else:
            path, _ = QtWidgets.QFileDialog.getOpenFileName(
                dir=os.path.expandvars(os.path.expanduser(self.__dir)),
                filter=self.__filters,
                caption=self.__caption,
            )
        if path:
            self.path_edit.setText(path)

    @classmethod
    def datatype(cls):
        return "file"

    def setup(self, parameter: Parameter):
        super().setup(parameter)
        metadata = parameter.metadata()
        if metadata.get("save"):
            self.__save_file = True
            self.pick_button.setIcon(qta.icon("fa5s.save"))

        if metadata.get("filters"):
            self.__filters = metadata["filters"]

        if metadata.get("dir"):
            self.__initial_dir = metadata["dir"]

        if metadata.get("caption"):
            self.__caption = metadata["caption"]

    def value(self):
        return self.path_edit.text()

    def setValue(self, value):
        self.path_edit.setText(value)
