import json
import os
import typing

import qtawesome as qta

from PySide6 import QtWidgets, QtGui, QtCore

from radium.nodegraph.graph import NodeGraphController
from radium.nodegraph.graph.view import NodeGraphView
from radium.nodegraph.browser import NodeBrowserView
from radium.nodegraph.factory import prototypes
from radium.nodegraph.factory import NodeFactory
from radium.nodegraph.parameters import ParameterEditorController, ParameterEditorView


class MainController(QtCore.QObject):
    """
    This controller acts as glue between the main window and the node graph. It also provides loading/saving support
    and some basic keyboard shortcuts via QActions.
    """

    def __init__(self):
        super().__init__()
        self.__dirty = False
        self.settings = QtCore.QSettings("radium", "nodegraph.demo")
        self.undo_stack = QtGui.QUndoStack()
        self.node_factory = NodeFactory()

        self.node_graph_view = NodeGraphView()
        self.node_graph_controller = NodeGraphController(
            undo_stack=self.undo_stack, node_factory=self.node_factory
        )
        self.node_graph_controller.attachView(self.node_graph_view)

        self.node_browser_view = NodeBrowserView()
        self.node_browser_view.setModel(self.node_factory.node_types_model)

        self.parameter_editor_view = ParameterEditorView()
        self.parameter_editor_controller = ParameterEditorController()
        self.parameter_editor_controller.attachView(self.parameter_editor_view)

        self.central_widget = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.central_widget.addWidget(self.node_browser_view)
        self.central_widget.addWidget(self.node_graph_view)
        self.central_widget.addWidget(self.parameter_editor_view)

        self.main_window = QtWidgets.QMainWindow()
        self.main_window.setCentralWidget(self.central_widget)

        self.file_menu = self.main_window.menuBar().addMenu("&File")
        self.edit_menu = self.main_window.menuBar().addMenu("&Edit")

        self.recent_files_menu = QtWidgets.QMenu("Recent")
        self.recent_files_menu.aboutToShow.connect(self.rebuildRecentFilesMenu)

        self.__current_filename = None
        self.__recent_files: typing.List[str] = json.loads(
            self.settings.value("recent_files", "[]")
        )

        self.initMenuBar()
        self.initNodes()

        self.undo_stack.cleanChanged.connect(self.updateWindowTitle)
        self.node_graph_controller.scene.selectionChanged.connect(
            self.onSelectionChanged
        )

    def onSelectionChanged(self):
        selection = self.node_graph_controller.scene.selectedNodes()

        if selection:
            self.parameter_editor_controller.setNode(selection[0])
        else:
            self.parameter_editor_controller.clear()

    def initNodes(self):
        """
        Register some basic example nodes. Nodes prototypes must be registered
        before they can be created.
        """
        self.node_factory.registerPortType(
            prototypes.PortType(
                "image",
                color=(0, 127, 0, 255),
                outline_color=(0, 100, 0, 255),
            )
        )

        self.node_factory.registerNodeType(
            prototypes.NodeType(
                name="Merge",
                category="Nodes",
                inputs={
                    "image_a": "image",
                    "image_b": "image",
                },
                outputs={"image": "image"},
                parameters={
                    "blend": prototypes.ParameterPrototype(
                        name="blend",
                        value=0.5,
                        datatype="float",
                    )
                },
            )
        )
        self.node_factory.registerNodeType(
            prototypes.NodeType(
                name="Constant",
                category="Nodes",
                outputs={"image": "image"},
                parameters={
                    "color": prototypes.ParameterPrototype(
                        name="color",
                        value=[127, 127, 127, 255],
                        datatype="RGBA",
                    )
                },
                icon="fa.image",
            )
        )

        self.node_factory.registerNodeType(
            prototypes.NodeType(
                name="LoadImage",
                category="Nodes",
                outputs={"image": "image"},
                icon="fa.file",
            )
        )

    def initMenuBar(self):
        """
        Initialise the main windows menu bar
        """
        open_action = QtGui.QAction("&Open", self)
        open_action.setIcon(qta.icon("fa.file"))
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.onOpenAction)
        self.file_menu.addAction(open_action)

        self.file_menu.addMenu(self.recent_files_menu)

        save_action = QtGui.QAction("&Save", self)
        save_action.setIcon(qta.icon("fa.save"))
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.onSaveAction)
        self.file_menu.addAction(save_action)

        save_as_action = QtGui.QAction("Save As...", self)
        save_as_action.setIcon(qta.icon("fa.save"))
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(lambda: self.onSaveAction(save_as=True))
        self.file_menu.addAction(save_as_action)

        reset_action = QtGui.QAction("&Reset", self)
        reset_action.setIcon(qta.icon("ei.asterisk"))
        reset_action.setShortcut("Ctrl+R")
        reset_action.triggered.connect(self.onResetAction)
        self.file_menu.addAction(reset_action)

        undo_action = self.undo_stack.createUndoAction(self)
        undo_action.setIcon(qta.icon("fa5s.undo"))
        undo_action.setShortcut("Ctrl+Z")
        self.edit_menu.addAction(undo_action)

        redo_action = self.undo_stack.createRedoAction(self)
        redo_action.setIcon(qta.icon("fa5s.redo"))
        redo_action.setShortcut("Ctrl+Y")
        self.edit_menu.addAction(redo_action)

        delete_action = QtGui.QAction("&Delete", self)
        delete_action.setIcon(qta.icon("fa.remove"))
        delete_action.setShortcut("Delete")

        delete_action.triggered.connect(self.onDeleteAction)
        self.edit_menu.addAction(delete_action)

    def __storeRecentFile(self, filename):
        """
        Store a recent file in the demo apps settings.
        """

        if filename in self.__recent_files:
            self.__recent_files.remove(filename)

        self.__recent_files.insert(0, filename)

        if len(self.__recent_files) > 10:
            self.__recent_files = self.__recent_files[:10]

        self.settings.setValue("recent_files", json.dumps(self.__recent_files))

    @QtCore.Slot()
    def rebuildRecentFilesMenu(self):
        """
        When the recent files menu is about to show populate it with a list of recent files.
        """
        self.recent_files_menu.clear()

        for recent_file in self.__recent_files:
            action = QtGui.QAction(
                os.path.basename(recent_file), parent=self.recent_files_menu
            )
            action.setData(recent_file)
            action.triggered.connect(self.onRecentFileClicked)
            self.recent_files_menu.addAction(action)

    @QtCore.Slot()
    def onRecentFileClicked(self):
        action: QtGui.QAction = self.sender()
        path = action.data()
        self.onOpenAction(filename=path)

    @QtCore.Slot()
    def onResetAction(self):
        """
        When the reset action has triggered reset the graph.
        """
        if not self.undo_stack.isClean():
            reply = QtWidgets.QMessageBox.question(
                self.main_window,
                "Unsaved Changes",
                "Unsaved Changes will be lost. Continue?",
                QtWidgets.QMessageBox.StandardButton.Yes,
                QtWidgets.QMessageBox.StandardButton.No,
            )
            if reply == QtWidgets.QMessageBox.StandardButton.No:
                return False

        self.__current_filename = None
        self.node_graph_controller.scene.clear()
        self.undo_stack.clear()
        self.updateWindowTitle()
        return True

    @QtCore.Slot()
    def onOpenAction(self, *args, filename=None):
        """
        When the open action has triggered open the provided filename or prompt for one.
        """
        if not self.onResetAction():
            return

        print("loading filename", filename)

        if filename is None:
            self.__current_filename, _ = QtWidgets.QFileDialog.getOpenFileName(
                self.main_window,
                "Open File",
                filter="*.json file(*.json)",
                dir=str(self.settings.value("last_open_directory", os.getcwd())),
            )
        else:
            self.__current_filename = filename

        if not self.__current_filename:
            return

        self.settings.setValue(
            "last_open_directory", os.path.dirname(self.__current_filename)
        )

        with open(self.__current_filename, "r") as f:
            data = json.load(f)

        self.__storeRecentFile(self.__current_filename)

        self.node_graph_controller.scene.loadDict(data, self.node_factory)
        self.updateWindowTitle()

    def updateWindowTitle(self):
        """
        Update the main windows title to reflect the state of the application.
        This sets the current filename and marks if it is unsaved.
        """
        if self.undo_stack.isClean():
            suffix = ""
        else:
            suffix = "*"

        if self.__current_filename:
            prefix = os.path.basename(self.__current_filename)
        else:
            prefix = "Unsaved File"

        self.main_window.setWindowTitle(f"{prefix}{suffix}")

    @QtCore.Slot()
    def onSaveAction(self, *_, save_as=False):
        """
        When the save action has triggered save the current file. If save_as is set then save as a new filename.
        """
        if self.__current_filename is None or save_as:
            self.__current_filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self.main_window,
                "Save File",
                filter="*.json file(*.json)",
                dir=str(self.settings.value("last_save_directory", os.getcwd())),
            )

            if not self.__current_filename:
                return

            self.settings.setValue(
                "last_save_directory", os.path.dirname(self.__current_filename)
            )

        data = self.node_graph_controller.scene.dumpDict()
        with open(self.__current_filename, "w") as f:
            json.dump(data, f)

        self.undo_stack.setClean()
        self.__storeRecentFile(self.__current_filename)
        self.updateWindowTitle()

    @QtCore.Slot()
    def onDeleteAction(self):
        """
        When the delete action has triggered delete the currently selected nodes.
        """
        selection = self.node_graph_controller.scene.selectedNodes()
        self.undo_stack.beginMacro("Delete Selected Nodes")
        for node in selection:
            self.node_graph_controller.removeItem(node)
        self.undo_stack.endMacro()
