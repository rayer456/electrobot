import sys
import os
import json

from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QListWidgetItem
from PyQt6.QtGui import QIcon

from prediction_window_ui import Ui_MainWindow
from LiveSplitData import LiveSplitData


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Predictions Manager v2")
        self.connectFunctions()

        self.checkAndLoadData()
        self.listOutcomes()
        self.refreshCatList()
        self.setActiveCategory()

        
    def connectFunctions(self):
        self.actionOpen.triggered.connect(self.selectFile)
        self.categoryList.itemClicked.connect(lambda: self.refreshSplitList())
        self.splitList.itemSelectionChanged.connect(self.loadPredictionForm)
        self.setActiveButton.clicked.connect(lambda: self.setActiveCategory(setActive=True))
        self.saveButton.clicked.connect(self.savePrediction)
        self.deleteButton.clicked.connect(self.deletePrediction)
        self.removeCatButton.clicked.connect(self.removeSelectedCategory)

        #on user edit
        self.field_name.textEdited.connect(self.inputChange)
        self.field_autoStart.clicked.connect(self.inputChange)
        self.field_splitName.textEdited.connect(self.inputChange)
        self.field_title.textEdited.connect(self.inputChange)
        self.field_outcome1.textEdited.connect(self.inputChange)
        self.field_outcome2.textEdited.connect(self.inputChange)
        self.field_outcome3.textEdited.connect(self.inputChange)
        self.field_outcome4.textEdited.connect(self.inputChange)
        self.field_outcome5.textEdited.connect(self.inputChange)
        self.field_outcome6.textEdited.connect(self.inputChange)
        self.field_outcome7.textEdited.connect(self.inputChange)
        self.field_outcome8.textEdited.connect(self.inputChange)
        self.field_outcome9.textEdited.connect(self.inputChange)
        self.field_outcome10.textEdited.connect(self.inputChange)
        self.field_window.textEdited.connect(self.inputChange)


    def checkAndLoadData(self):
        if not os.path.exists('predictions'):
            os.makedirs('predictions')

        while True:
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


    def refreshCatList(self, setIndexTo=0, activeClicked=False):
        self.categoryList.clear()

        for cat in self.all_data['cats']:
            catRow = QListWidgetItem(cat['category'])
            if cat['active']:
                catRow.setIcon(QIcon('assets/star.png'))

            self.categoryList.addItem(catRow)

        self.categoryList.setCurrentRow(setIndexTo)
        if len(self.all_data['cats']) > 0:
            if activeClicked:
                self.refreshSplitList(self.splitList.currentRow())
            else:
                self.refreshSplitList()
        else:
            self.splitList.blockSignals(True)
            self.splitList.clear()
            self.splitList.blockSignals(False)

    
    def refreshSplitList(self, setIndexTo=0):
        self.splitList.clear()
        selected_cat = self.categoryList.currentItem().text()

        for cat in self.all_data['cats']:
            if cat['category'] == selected_cat:
                for split in cat['split_names']:
                    splitRow = QListWidgetItem(split['split_name'])
                    if split['prediction']:
                        splitRow.setIcon(QIcon('assets/star.png'))
                    
                    self.splitList.addItem(splitRow)
                break

        self.splitList.setCurrentRow(setIndexTo)


    def setActiveCategory(self, setActive=False):
            # replace existing one
            if hasattr(self, 'activeCategory') and setActive:
                try:
                    self.activeCategory = self.categoryList.currentItem().text()
                except AttributeError:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setText("No category selected")
                    msg.setWindowTitle("Warning")
                    msg.exec()
                    return
                
                for cat in self.all_data['cats']:
                    if cat['category'] == self.activeCategory:
                        cat['active'] = True
                    else:
                        cat['active'] = False
            # initial
            else:
                for cat in self.all_data['cats']:
                    if cat['active']:
                        self.activeCategory = cat['category']
                        break
                # no active cat
                else:
                    self.activeCategory = None
            
            self.activeCategoryText.setText(f'Active Category: {self.activeCategory}')         

            if setActive:
                self.refreshCatList(self.categoryList.currentRow(), activeClicked=True)
                self.save_all_data()
                self.saveToPredFile()


    def selectFile(self):
        paths, ext = QFileDialog.getOpenFileNames(
            self,
            caption='Select one or more Livesplit files',
            filter='*.lss'
        )

        if len(paths) == 0:
            return

        self.add_cats_to_datafile(paths)


    def add_cats_to_datafile(self, paths: list):
        namesToAdd, catsToAdd = [], []

        for path in paths:
            lsd = LiveSplitData(path=path)
            subcategory = lsd.get_subcategory()

            for name in namesToAdd:
                if name == subcategory:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setText(f"Can't add {subcategory} more than once")
                    msg.setWindowTitle("Warning")
                    msg.exec()
                    return
            for cat in self.all_data['cats']:
                if cat['category'] == subcategory:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setText(f"{subcategory} is already in the list")
                    msg.setWindowTitle("Warning")
                    msg.exec()
                    return
            
            # list of objects each containing split name and empty prediction
            splits_with_preds = [{
                'split_name': split_name,
                'prediction': {},
            } for split_name in lsd.get_split_names()]

            new_cat = {
                'category': subcategory,
                'active': False, # only active if user sets it
                'split_names': splits_with_preds
            }

            namesToAdd.append(subcategory)
            catsToAdd.append(new_cat)
        
        self.all_data['cats'].extend(catsToAdd)
        self.save_all_data()
        self.refreshCatList()


    def loadPredictionForm(self):
        selected_cat = self.categoryList.currentItem().text()
        selected_split = self.splitList.currentItem().text()

        #TODO create separate function to find cat and split?
        for cat in self.all_data['cats']:
            if cat['category'] == selected_cat:
                for split in cat['split_names']:
                    if split['split_name'] == selected_split:
                        self.resetFields()

                        if split['prediction']: # if prediction present
                            self.populateFields(split['prediction'], selected_split)

                        self.savedStatus.setText('Status: Saved')
                        self.savedStatus.setStyleSheet("QLabel {\n"
                        "    color: darkgreen;\n"
                        "}")
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


    def resetFields(self):
        self.field_name.clear()
        self.field_autoStart.setChecked(True)
        self.field_splitName.setText(self.splitList.currentItem().text())
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


    def inputChange(self):
        self.savedStatus.setText("Status: Unsaved")    
        self.savedStatus.setStyleSheet("QLabel {\n"
        "    color: orange;\n"
        "}")


    def savePrediction(self):
        try:
            old_selected_split = self.splitList.currentItem().text()
        except AttributeError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("No split selected")
            msg.setWindowTitle("Warning")
            msg.exec()
            return
        
        formIsValid = self.validateForm(old_selected_split)

        if formIsValid:
            all_cats: list = self.all_data['cats']
            selected_cat = self.categoryList.currentItem().text()
            selected_split = self.splitList.currentItem().text()
            
            for cat in all_cats:
                if cat['category'] == selected_cat:
                    for split in cat['split_names']:
                        if split['split_name'] == old_selected_split:
                            # replace split name
                            split['split_name'] = selected_split
                            new_prediction = {
                                'auto_predict': {
                                    'auto_start': self.field_autoStart.isChecked(),
                                    'split_name': self.field_splitName.text()
                                },
                                'data': {
                                    'broadcaster_id': '',
                                    'outcomes': [],
                                    'prediction_window': int(self.field_window.text()),
                                    'title': self.field_title.text(),
                                },
                                'name': self.field_name.text(),
                            }

                            for outcome in self.outcomes:
                                if outcome.text() != '':
                                    new_prediction['data']['outcomes'].append(
                                        {
                                            'title': outcome.text()
                                        }
                                    )

                            split['prediction'] = new_prediction
                            break
                    break
            
            self.refreshSplitList(self.splitList.currentRow())
            self.save_all_data()
            self.savedStatus.setText('Status: Saved')
            self.savedStatus.setStyleSheet("QLabel {\n"
            "    color: darkgreen;\n"
            "}")
            if self.activeCategory == selected_cat:
                self.saveToPredFile()


    def deletePrediction(self):
        try:
            selected_cat = self.categoryList.currentItem().text()
            selected_split = self.splitList.currentItem().text()
        except AttributeError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("No split selected")
            msg.setWindowTitle("Warning")
            msg.exec()
            return

        for cat in self.all_data['cats']:
            if cat['category'] == selected_cat:
                for split in cat['split_names']:
                    if split['split_name'] == selected_split:
                        split['prediction'] = {}
                        break
                break

        self.resetFields()
        self.refreshSplitList(self.splitList.currentRow())
        self.save_all_data()
        if self.activeCategory == selected_cat:
            self.saveToPredFile()
        self.savedStatus.setText('Status: Deleted')
        self.savedStatus.setStyleSheet("QLabel {\n"
        "    color: darkred;\n"
        "}")


    def save_all_data(self):
        with open('predictions/all_data.json', 'w') as file:
            file.write(json.dumps(self.all_data))


    def saveToPredFile(self):
        predictions = {
            'predictions': []
        }

        # get all preds of the active category
        for cat in self.all_data['cats']:
            if cat['active']:
                for split in cat['split_names']:
                    if split['prediction']:
                        predictions['predictions'].append(split['prediction'])
                break
               
        with open('predictions/predictions.json', 'w') as file:
            file.write(json.dumps(predictions))

    
    def validateForm(self, selected_split) -> bool:

        name = self.field_name.text()
        title = self.field_title.text()
        splitName = self.field_splitName.text()
        
        # name
        if len(name.split()) != 1:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Name must be one word")
            msg.setWindowTitle("Invalid name")
            msg.exec()
            return 0

        # title
        if title == '':
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Must set a Title")
            msg.setWindowTitle("No title")
            msg.exec()
            return 0
        
        # split name
        if splitName == '':
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Must set a Split name")
            msg.setWindowTitle("No Split name")
            msg.exec()
            return 0
        
        if splitName != selected_split:
            choice = QMessageBox().question(self, 'Difference detected', f'Field Split Name is different than the one in the splits. \n\nDo you want to replace the split name in the splits with the Split Name field? (Probably yes) \n{selected_split} --> {splitName}')

            if choice == QMessageBox.StandardButton.Yes:
                # duplicate split name
                for cat in self.all_data['cats']:
                    if cat['category'] == self.categoryList.currentItem().text():
                        for split in cat['split_names']:
                            if split['split_name'] == splitName:
                                msg = QMessageBox()
                                msg.setIcon(QMessageBox.Icon.Warning)
                                msg.setText("Can't have duplicate split names")
                                msg.setWindowTitle("Duplicate split name")
                                msg.exec()
                                self.field_splitName.setText(selected_split)
                                return 0

                self.splitList.currentItem().setText(splitName)
            else:
                self.field_splitName.setText(selected_split)
                return 0

        # outcomes
        outcome_counter = 0
        for outcome in self.outcomes:
            if outcome.text() != '':
                outcome_counter += 1
        
        if outcome_counter < 2:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Must have at least 2 outcomes")
            msg.setWindowTitle("Not enough outcomes")
            msg.exec()
            return 0

        # window
        try:
            window = int(self.field_window.text())
            if not 30 <= window <= 1800:
                raise ValueError
        except ValueError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Window must be a number between 30 and 1800")
            msg.setWindowTitle("Invalid value")
            msg.exec()
            return 0
    
        return 1

    def removeSelectedCategory(self):
        selected = self.categoryList.currentRow()

        try:
            selected_cat = self.categoryList.currentItem().text()
        except AttributeError:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setText("No category selected")
                msg.setWindowTitle("Warning")
                msg.exec()
                return
    
        self.categoryList.takeItem(selected)

        activeCat = False
        for i, cat in enumerate(self.all_data['cats']):
            if cat['category'] == selected_cat:
                if cat['active']:
                    activeCat = True
                self.all_data['cats'].pop(i)
                break

        self.refreshCatList()
        self.setActiveCategory()
        self.save_all_data()
        if activeCat:
            self.saveToPredFile()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())