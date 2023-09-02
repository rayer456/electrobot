import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QSizePolicy

from prediction_window_ui import Ui_MainWindow


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Predictions Manager")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
        