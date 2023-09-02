import sys
import os

from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QSizePolicy

from prediction_window_ui import Ui_MainWindow
from LiveSplitData import LiveSplitData


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Predictions Manager")
        self.connectFunctions()

    def connectFunctions(self):
        self.actionOpen.triggered.connect(self.selectFile)
        # load existing data if data file exists

        self.setActiveButton.clicked.connect(self.setCategoryAsActive)
        self.saveButton.clicked.connect(self.savePrediction)
        self.deleteButton.clicked.connect(self.deletePrediction)

    def selectFile(self):
        fileDialog = QFileDialog.getOpenFileNames(
            self,
            caption='Select one or more Livesplit files',
            filter='*.lss'
        )
        paths = fileDialog[0]
        if isinstance(paths, str):
            if paths == '':
                return
            paths = list(paths)
        
        self.add_lss_to_datafile(paths)

    def add_lss_to_datafile(self, paths: list):
        for path in paths:
            lsd = LiveSplitData(path=path)
            


    def setCategoryAsActive():
        pass

    def savePrediction():
        pass

    def deletePrediction():
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
        