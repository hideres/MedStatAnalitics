import sys
from PyQt6 import QtWidgets, QtGui
from app_window import MainWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    app.setWindowIcon(QtGui.QIcon("data/medstat.jpg"))
    exit_icon = QtGui.QIcon("data/exit.png")

    window = MainWindow(exit_icon=exit_icon)
    window.show()
    sys.exit(app.exec())