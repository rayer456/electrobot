import sys
import os
import json

from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QSizePolicy, QLineEdit

from prediction_window_ui import Ui_MainWindow
from LiveSplitData import LiveSplitData


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Predictions Manager")

        self.connectFunctions()

        self.checkAndLoadData()
        self.loadCatsInList()
        self.listOutcomes()


    def connectFunctions(self):
        self.actionOpen.triggered.connect(self.selectFile)
        
        self.categoryList.itemClicked.connect(self.loadSplitList)
        self.splitList.itemSelectionChanged.connect(self.loadPredictionForm)
        self.setActiveButton.clicked.connect(self.setCategoryAsActive)
        self.saveButton.clicked.connect(self.savePrediction)
        self.deleteButton.clicked.connect(self.deletePrediction)


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


    def loadCatsInList(self):
        self.categoryList.clear()
        all_cats: list = self.all_data['cats']
        for cat in all_cats:
            self.categoryList.addItem(cat['category'])


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
        
        self.add_cats_to_datafile(paths)


    def add_cats_to_datafile(self, paths: list):

        for path in paths:
            lsd = LiveSplitData(path=path)
            subcategory = lsd.get_subcategory()

            for cat in self.all_data['cats']:
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

            self.all_data['cats'].append(new_cat)

        
        with open('predictions/all_data.json', 'w') as file:
            file.write(json.dumps(self.all_data))

        self.loadCatsInList()

    
    def listOutcomes(self):
        self.outcomes = [self.field_outcome1]
        self.outcomes.append(self.field_outcome2)
        self.outcomes.append(self.field_outcome3)
        self.outcomes.append(self.field_outcome4)
        self.outcomes.append(self.field_outcome5)
        self.outcomes.append(self.field_outcome6)
        self.outcomes.append(self.field_outcome7)
        self.outcomes.append(self.field_outcome8)
        self.outcomes.append(self.field_outcome9)
        self.outcomes.append(self.field_outcome10)


    def loadSplitList(self):
        self.splitList.clear()
        selected_cat = self.categoryList.currentItem().text()

        for cat in self.all_data['cats']:
            if cat['category'] == selected_cat:
                for split in cat['split_names']:
                    self.splitList.addItem(split['split_name'])
                break

        self.splitList.setCurrentRow(0)


    def loadPredictionForm(self):
        selected_cat = self.categoryList.currentItem().text()
        selected_split = self.splitList.currentItem().text()

        #TODO create separate function to find cat and split?
        for cat in self.all_data['cats']:
            if cat['category'] == selected_cat:
                for split in cat['split_names']:
                    if split['split_name'] == selected_split:
                        if bool(split['prediction']): # if prediction present
                            self.resetFields()
                            self.populateFields(p=split['prediction'], split_name=split['split_name'])
                        else:
                            self.resetFields(split_name=split['split_name'])
                                
                        break
                break

    
    def populateFields(self, p, split_name):
        self.field_name.setText(p['name'])
        self.field_autoStart.setChecked(p['auto_predict']['auto_start'])
        self.field_splitName.setText(split_name)
        self.field_title.setText(p['data']['title'])

        pred_outcomes = p['data']['outcomes']
        for i, pred_outcome in enumerate(pred_outcomes):
            self.outcomes[i].setText(pred_outcome['title'])

        self.field_window.setText(str(p['data']['prediction_window']))


    def resetFields(self, split_name=''):
        self.field_name.clear()
        self.field_autoStart.setChecked(True)
        self.field_splitName.setText(split_name)
        self.field_title.clear()
        self.field_outcome1.clear()
        self.field_outcome2.clear()
        self.field_outcome3.clear()
        self.field_outcome4.clear()
        self.field_outcome5.clear()
        self.field_outcome6.clear()
        self.field_outcome7.clear()
        self.field_outcome8.clear()
        self.field_outcome9.clear()
        self.field_outcome10.clear()
        self.field_window.clear()

        
    def setCategoryAsActive(self):
        # write to predictions.json
        pass


    def savePrediction(self):
        pass
        self.validateForm()


    def deletePrediction(self):
        pass

    
    def validateForm(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
        