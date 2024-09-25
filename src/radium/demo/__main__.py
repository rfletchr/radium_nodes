import os
import sys
import qtawesome as qta
from PySide6 import QtWidgets

from radium.demo.controller import MainController


def main():
    os.environ["QT_QPA_PLATFORM"] = "xcb"
    app = QtWidgets.QApplication()
    app.setApplicationDisplayName("Radium Demo")
    app.setApplicationName("Radium Demo")
    app.setWindowIcon(qta.icon("fa5s.radiation-alt"))

    controller = MainController()
    controller.main_window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
