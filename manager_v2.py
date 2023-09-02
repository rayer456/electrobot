import sys
import os
import json

from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QSizePolicy

from prediction_window_ui import Ui_MainWindow
from LiveSplitData import LiveSplitData


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.checkAndLoadData()
        self.setupUi(self)
        self.setWindowTitle("Predictions Manager")
        self.connectFunctions()


    def checkAndLoadData(self):
        if not os.path.exists('predictions'):
            os.makedirs('predictions')

        while 1:
            try:
                with open('predictions/all_data.json', 'r') as file:
                    self.all_data: dict = json.load(file)
                    break
            except FileNotFoundError:
                default = {
                    'cats': []
                }
                with open('predictions/all_data.json', 'w') as file:
                    file.write(json.dumps(default))


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
        all_cats: list = self.all_data['cats']

        for path in paths:
            lsd = LiveSplitData(path=path)
            subcategory = lsd.get_subcategory()

            for cat in all_cats:
                if cat['category'] == subcategory:
                    print("Category is already in the list of categories")
                    return

            # list of objects containing split name and empty object
            splits_with_preds = [{
                'split_name': split_name,
                'prediction': {},
            } for split_name in lsd.get_split_names()]

            new_cat = {
                'category': f'{subcategory}',
                'active': False, # only active if user sets it
                'split_names': splits_with_preds
            }
            all_cats.append(new_cat)

        to_write = {
                    'cats': all_cats
                }
        
        with open('predictions/all_data.json', 'w') as file:
            file.write(json.dumps(to_write))
        


    def setCategoryAsActive():
        # write to predictions.json
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
        