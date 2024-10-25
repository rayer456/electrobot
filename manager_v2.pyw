import sys
import os
import json

from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QListWidgetItem
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from src import Ui_MainWindow
from src import LiveSplitData
from src import Prediction
from src import Category


ALL_DATA_PATH = "predictions/all_data.json"
PREDICTIONS_PATH = "predictions/predictions.json"

class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Predictions Manager v2")
        self.connectFunctions()

        self.checkAndLoadData()
        self.putOutcomesInList()
        self.refreshCatList()
        self.setActiveCategory()

        
    def connectFunctions(self):
        self.actionOpen.triggered.connect(self.selectFile)
        
        # will pass index parameter when triggered like this
        self.categoryList.itemClicked.connect(lambda: self.refreshSplitList())
        self.splitList.itemSelectionChanged.connect(self.loadPredictionForm)
        self.setActiveButton.clicked.connect(lambda: self.setActiveCategory(setActive=True))
        self.saveButton.clicked.connect(self.savePrediction)
        self.deleteButton.clicked.connect(self.deletePrediction)
        self.removeCatButton.clicked.connect(self.removeSelectedCategory)

        # on user edit
        self.field_name.textEdited.connect(self.statusChange)
        self.field_autoStart.clicked.connect(self.statusChange)
        self.field_splitName.textEdited.connect(self.statusChange)
        self.field_title.textEdited.connect(self.statusChange)
        self.field_outcome1.textEdited.connect(self.statusChange)
        self.field_outcome2.textEdited.connect(self.statusChange)
        self.field_outcome3.textEdited.connect(self.statusChange)
        self.field_outcome4.textEdited.connect(self.statusChange)
        self.field_outcome5.textEdited.connect(self.statusChange)
        self.field_outcome6.textEdited.connect(self.statusChange)
        self.field_outcome7.textEdited.connect(self.statusChange)
        self.field_outcome8.textEdited.connect(self.statusChange)
        self.field_outcome9.textEdited.connect(self.statusChange)
        self.field_outcome10.textEdited.connect(self.statusChange)
        self.field_window.textEdited.connect(self.statusChange)


    def checkAndLoadData(self):
        if not os.path.exists('predictions'):
            os.makedirs('predictions')

        if not os.path.exists(ALL_DATA_PATH):
            default = {
                'cats': []
            }
            with open(ALL_DATA_PATH, 'w') as file:
                file.write(json.dumps(default))

        try:
            with open(ALL_DATA_PATH, 'r') as file:
                all_cats_serialized: list[dict] = json.load(file).copy()["cats"]
        except Exception:
            dialog = QMessageBox(self)
            dialog.setWindowTitle("Alert")
            dialog.setText(f"Couldn't load {ALL_DATA_PATH}\n\nClosing...")
            button = dialog.exec()

            if button == QMessageBox.StandardButton.Ok:
                exit(1)
            
        self.deserialized_cats: list[Category] = []
        for cat_ser in all_cats_serialized:
            split_predictions: list[Prediction] = []
            for pred in cat_ser["split_names"]:
                pred: dict

                is_empty=False
                if not pred["prediction"]:
                    is_empty = True

                # form prediction based on data in file
                # even if it's empty
                prediction = Prediction(
                    split_name=pred["split_name"],
                    auto_start=pred.get('prediction', {}).get('auto_start', False),
                    pred_split_name=pred.get("prediction", {}).get("split_name", ""),
                    pred_name=pred.get("prediction", {}).get("name", ""),
                    data_to_send=pred.get("prediction", {}).get("data", {}),
                    is_empty=is_empty,
                )
                split_predictions.append(prediction)

            # split predictions are templates containing an empty prediction and a split name
            category = Category(
                active=cat_ser["active"],
                category=cat_ser["category"],
                game_name=cat_ser["game_name"],
                split_predictions=split_predictions,
            )
            self.deserialized_cats.append(category)
        

    def putOutcomesInList(self):
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

        for cat in self.deserialized_cats:
            cat_row = QListWidgetItem(cat.category)
            cat_row.setData(Qt.ItemDataRole.UserRole, cat.game_name)
            if cat.active:
                cat_row.setIcon(QIcon('assets/star.png'))

            self.categoryList.addItem(cat_row)

        self.categoryList.setCurrentRow(setIndexTo)
        if len(self.deserialized_cats) > 0:
            if activeClicked:
                self.refreshSplitList(self.splitList.currentRow())
            else:
                self.refreshSplitList()
        else:
            self.splitList.blockSignals(True)
            self.splitList.clear()
            self.splitList.blockSignals(False)

    
    def refreshSplitList(self, setIndexTo=0):
        # self.splitList.blockSignals(True)
        self.splitList.clear()
        # self.splitList.blockSignals(False) #itemSelectionChanged signal triggers here
        selected_cat = self.categoryList.currentItem().text()
        selected_cat_game_name = self.categoryList.currentItem().data(Qt.ItemDataRole.UserRole)

        for cat in self.deserialized_cats:
            if cat.category == selected_cat and cat.game_name == selected_cat_game_name:
                for split in cat.split_predictions:
                    split: Prediction
                    splitRow = QListWidgetItem(split.split_name)
                    if not split.is_empty:
                        splitRow.setIcon(QIcon('assets/star.png'))

                    self.splitList.addItem(splitRow)
                break

        self.splitList.setCurrentRow(setIndexTo)


    def setActiveCategory(self, setActive=False):
            # replace existing one
            if hasattr(self, 'activeCategory') and setActive:
                try:
                    self.activeCategory = self.categoryList.currentItem().text()
                    selected_cat_game_name = self.categoryList.currentItem().data(Qt.ItemDataRole.UserRole)
                except AttributeError:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setText("No category selected")
                    msg.setWindowTitle("Warning")
                    msg.exec()
                    return
                
                for cat in self.deserialized_cats:
                    if cat.game_name == selected_cat_game_name:
                        cat.active = cat.category == self.activeCategory
                    else:
                        cat.active = False

            # initial
            else:
                for cat in self.deserialized_cats:
                    if cat.active:
                        self.activeCategory = cat.category
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
        cats_to_add = []

        for path in paths:
            lsd = LiveSplitData(path)
            subcategory = lsd.get_subcategory()
            game_name = lsd.get_game_name()

            for cat in self.deserialized_cats:
                if cat.category == subcategory and cat.game_name == game_name:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setText(f"{subcategory} from {game_name} is already in the list")
                    msg.setWindowTitle("Warning")
                    msg.exec()
                    return
            
            # list of objects each containing split name and empty prediction
            split_preds = [Prediction.empty(split_name) for split_name in lsd.get_split_names()]

            new_cat = Category(
                active=False, # only active if user sets it
                game_name=game_name,
                category=subcategory,
                split_predictions=split_preds
            )

            cats_to_add.append(new_cat)
        
        self.deserialized_cats.extend(cats_to_add)
        self.save_all_data()
        self.refreshCatList()


    def loadPredictionForm(self):
        selected_cat = self.categoryList.currentItem().text()
        selected_split = self.splitList.currentItem().text()
        selected_cat_game_name = self.categoryList.currentItem().data(Qt.ItemDataRole.UserRole)

        #TODO create separate function to find cat and split?
        for cat in self.deserialized_cats:
            if cat.category == selected_cat and cat.game_name == selected_cat_game_name:
                for split in cat.split_predictions:
                    split: Prediction
                    if split.split_name == selected_split:
                        self.resetFields()
                        # only populate fields of filled in predictions
                        if not split.is_empty:
                            self.populateFields(split, selected_split)

                        self.savedStatus.setText('Status: Saved')
                        self.savedStatus.setStyleSheet("QLabel {\n"
                        "    color: darkgreen;\n"
                        "}")
                        break
                break

    
    def populateFields(self, p: Prediction, split_name):
        self.field_name.setText(p.pred_name)
        self.field_autoStart.setChecked(p.auto_start)
        self.field_splitName.setText(split_name)
        self.field_title.setText(p.data_to_send['title'])
        
        pred_outcomes: list[dict] = p.data_to_send['outcomes']
        for i, pred_outcome in enumerate(pred_outcomes):
            self.outcomes[i].setText(pred_outcome['title'])

        self.field_window.setText(str(p.data_to_send['prediction_window']))


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


    def statusChange(self):
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
            selected_cat = self.categoryList.currentItem().text()
            selected_split = self.splitList.currentItem().text()
            selected_cat_game_name = self.categoryList.currentItem().data(Qt.ItemDataRole.UserRole)
            
            for cat in self.deserialized_cats:
                if cat.category == selected_cat and cat.game_name == selected_cat_game_name:
                    for i, split in enumerate(cat.split_predictions):
                        split: Prediction
                        if split.split_name == old_selected_split:
                            # replace split name
                            split.split_name = selected_split
                            new_prediction = Prediction(
                                split_name=self.field_splitName.text(),
                                auto_start=self.field_autoStart.isChecked(),
                                pred_split_name=self.field_splitName.text(),
                                pred_name=self.field_name.text(),
                                data_to_send={},
                                is_empty=False,
                            )
                            data_to_add = {
                                'broadcaster_id': '',
                                'outcomes': [],
                                'prediction_window': int(self.field_window.text()),
                                'title': self.field_title.text(),
                            }

                            for outcome in self.outcomes:
                                #TODO if outcome.text() ?
                                if outcome.text() != '':
                                    data_to_add['outcomes'].append(
                                        {
                                            'title': outcome.text()
                                        }
                                    )
                            new_prediction.data_to_send = data_to_add
                            cat.split_predictions[i] = new_prediction
                            break
                    break
            
            self.refreshSplitList(self.splitList.currentRow())
            self.save_all_data()
            if self.activeCategory == selected_cat:
                self.saveToPredFile()

            
            self.savedStatus.setText('Status: Saved')
            self.savedStatus.setStyleSheet("QLabel {\n"
            "    color: darkgreen;\n"
            "}")



    def deletePrediction(self):
        try:
            selected_cat = self.categoryList.currentItem().text()
            selected_split = self.splitList.currentItem().text()
            selected_cat_game_name = self.categoryList.currentItem().data(Qt.ItemDataRole.UserRole)
        except Exception:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("No split selected")
            msg.setWindowTitle("Warning")
            msg.exec()
            return

        # iterate over categories until selected category
        # iterate over splits until selected split
        for cat in self.deserialized_cats:
            if cat.category == selected_cat and cat.game_name == selected_cat_game_name:
                for split in cat.split_predictions:
                    split: Prediction
                    if split.split_name == selected_split:
                        split.reset()
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
        all_data = {
            "cats": [cat.as_json() for cat in self.deserialized_cats]
        }
        with open(ALL_DATA_PATH, 'w') as file:
            file.write(json.dumps(all_data))


    def saveToPredFile(self):
        predictions = {
            'predictions': []
        }
        # get all defined preds of the active category
        for cat in self.deserialized_cats:
            if cat.active:
                for split in cat.split_predictions:
                    split: Prediction
                    if not split.is_empty:
                        predictions['predictions'].append(split.pred_as_json())
                break
               
        with open(PREDICTIONS_PATH, 'w') as file:
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
        if len(title) < 1 or len(title) > 45:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Must set a Title with a maximum of 45 characters")
            msg.setInformativeText(f"You had {len(title)} characters")
            msg.setWindowTitle("Warning")
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
                for cat in self.deserialized_cats:
                    if cat.category == self.categoryList.currentItem().text():
                        for split in cat.split_predictions:
                            split: Prediction
                            if split.split_name == splitName:
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
            if 0 < len(outcome.text()) < 26:
                outcome_counter += 1
            elif len(outcome.text()) > 25:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setText("Title of an outcome must be at most 25 characters")
                msg.setWindowTitle("Warning")
                msg.exec()
                return 0
        
        if outcome_counter < 2:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Must have at least 2 outcomes")
            msg.setWindowTitle("Warning")
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
            selected_cat_game_name = self.categoryList.currentItem().data(Qt.ItemDataRole.UserRole)
        except AttributeError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("No category selected")
            msg.setWindowTitle("Warning")
            msg.exec()
            return
    
        self.categoryList.takeItem(selected)
        active_cat = False
        for i, cat in enumerate(self.deserialized_cats):
            if cat.category == selected_cat and cat.game_name == selected_cat_game_name:
                active_cat = cat.active
                self.deserialized_cats.pop(i)
                break

        self.refreshCatList()
        self.setActiveCategory()
        self.save_all_data()
        if active_cat:
            self.saveToPredFile()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())