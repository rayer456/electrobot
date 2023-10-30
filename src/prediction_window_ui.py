# Form implementation generated from reading ui file 'ui/manager.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 698)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(700, 0))
        MainWindow.setMaximumSize(QtCore.QSize(1100, 700))
        MainWindow.setBaseSize(QtCore.QSize(0, 0))
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setStyleSheet("QWidget {\n"
"    background-color: grey;\n"
"}\n"
"\n"
"QLineEdit {\n"
"    background-color: white;\n"
"    width: 100px;\n"
"    border-radius: 5px\n"
"}\n"
"\n"
"#saveButton {\n"
"    background-color: #0d7301;\n"
"    color: white;\n"
"    width: 100px;\n"
"    border-radius: 12px;\n"
"    outline: 0;\n"
"}\n"
"\n"
"#deleteButton {\n"
"    background-color: #a10000;\n"
"    color: white;\n"
"    width: 100px;\n"
"    border-radius: 12px;\n"
"    outline: 0;\n"
"}\n"
"\n"
"#saveButton:hover {\n"
"    background-color: green;\n"
"    color: white;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"#deleteButton:hover {\n"
"    background-color: red;\n"
"    color: white;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"#setActiveButton {\n"
"    background-color: #1e255d;\n"
"    color: white;\n"
"    width: 100px;\n"
"    border-radius: 12px;\n"
"    outline: 0;\n"
"}\n"
"\n"
"#setActiveButton:hover {\n"
"    background-color: #080a5d;\n"
"    color: white;\n"
"}")
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setHorizontalSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 20)
        self.mainLayout.setSpacing(15)
        self.mainLayout.setObjectName("mainLayout")
        self.categoriesLayout = QtWidgets.QVBoxLayout()
        self.categoriesLayout.setContentsMargins(-1, 0, -1, -1)
        self.categoriesLayout.setSpacing(0)
        self.categoriesLayout.setObjectName("categoriesLayout")
        self.categoriesLabel = QtWidgets.QLabel(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.categoriesLabel.sizePolicy().hasHeightForWidth())
        self.categoriesLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(False)
        font.setItalic(True)
        self.categoriesLabel.setFont(font)
        self.categoriesLabel.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.categoriesLabel.setAutoFillBackground(False)
        self.categoriesLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.categoriesLabel.setWordWrap(True)
        self.categoriesLabel.setObjectName("categoriesLabel")
        self.categoriesLayout.addWidget(self.categoriesLabel)
        self.categoryList = QtWidgets.QListWidget(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.categoryList.sizePolicy().hasHeightForWidth())
        self.categoryList.setSizePolicy(sizePolicy)
        self.categoryList.setMinimumSize(QtCore.QSize(130, 180))
        self.categoryList.setMaximumSize(QtCore.QSize(200, 16777215))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setKerning(True)
        self.categoryList.setFont(font)
        self.categoryList.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        self.categoryList.setMouseTracking(False)
        self.categoryList.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.categoryList.setStyleSheet("QListWidget {\n"
"    background-color: lightgrey;\n"
"    color: black;\n"
"    border-radius: 7px;\n"
"    outline: 0;\n"
"}\n"
"\n"
"QListWidget::item:selected {\n"
"    background-color: rgb(71, 29, 93);\n"
"    color: white;\n"
"}\n"
"\n"
"QListWidget:item:hover {\n"
"    background-color: rgb(71, 29, 93);\n"
"    color: white;\n"
"}\n"
"\n"
"\n"
"\n"
"")
        self.categoryList.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.categoryList.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked|QtWidgets.QAbstractItemView.EditTrigger.EditKeyPressed|QtWidgets.QAbstractItemView.EditTrigger.SelectedClicked)
        self.categoryList.setAlternatingRowColors(False)
        self.categoryList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.categoryList.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectItems)
        self.categoryList.setViewMode(QtWidgets.QListView.ViewMode.ListMode)
        self.categoryList.setSelectionRectVisible(False)
        self.categoryList.setObjectName("categoryList")
        self.categoriesLayout.addWidget(self.categoryList)
        self.removeCatButton = QtWidgets.QPushButton(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.removeCatButton.sizePolicy().hasHeightForWidth())
        self.removeCatButton.setSizePolicy(sizePolicy)
        self.removeCatButton.setMinimumSize(QtCore.QSize(80, 50))
        self.removeCatButton.setMaximumSize(QtCore.QSize(200, 50))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.removeCatButton.setFont(font)
        self.removeCatButton.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.removeCatButton.setStyleSheet("#removeCatButton {\n"
"    background-color: #a10000;\n"
"    color: white;\n"
"    width: 100px;\n"
"    border-radius: 12px;\n"
"    outline: 0;\n"
"}\n"
"\n"
"\n"
"#removeCatButton:hover {\n"
"    background-color: red;\n"
"    color: white;\n"
"    font-weight: bold;\n"
"}")
        self.removeCatButton.setObjectName("removeCatButton")
        self.categoriesLayout.addWidget(self.removeCatButton)
        self.mainLayout.addLayout(self.categoriesLayout)
        self.splitLayout = QtWidgets.QVBoxLayout()
        self.splitLayout.setContentsMargins(-1, 0, 0, 0)
        self.splitLayout.setSpacing(0)
        self.splitLayout.setObjectName("splitLayout")
        self.splitsLabel = QtWidgets.QLabel(parent=self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(False)
        font.setItalic(True)
        self.splitsLabel.setFont(font)
        self.splitsLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.splitsLabel.setWordWrap(True)
        self.splitsLabel.setObjectName("splitsLabel")
        self.splitLayout.addWidget(self.splitsLabel)
        self.splitList = QtWidgets.QListWidget(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitList.sizePolicy().hasHeightForWidth())
        self.splitList.setSizePolicy(sizePolicy)
        self.splitList.setMinimumSize(QtCore.QSize(130, 180))
        self.splitList.setMaximumSize(QtCore.QSize(200, 166666))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setKerning(True)
        self.splitList.setFont(font)
        self.splitList.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        self.splitList.setMouseTracking(False)
        self.splitList.setStyleSheet("QListWidget {\n"
"    background-color: lightgrey;\n"
"    color: black;\n"
"    border-radius: 7px;\n"
"    outline: 0;\n"
"}\n"
"\n"
"QListWidget::item:selected {\n"
"    color: white;\n"
"    background-color: rgb(71, 29, 93);\n"
"}\n"
"\n"
"QListWidget::item:hover {\n"
"    color: white;\n"
"    background-color: rgb(71, 29, 93);\n"
"}")
        self.splitList.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.splitList.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked|QtWidgets.QAbstractItemView.EditTrigger.EditKeyPressed|QtWidgets.QAbstractItemView.EditTrigger.SelectedClicked)
        self.splitList.setAlternatingRowColors(False)
        self.splitList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.splitList.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.splitList.setSelectionRectVisible(False)
        self.splitList.setObjectName("splitList")
        self.splitLayout.addWidget(self.splitList)
        self.mainLayout.addLayout(self.splitLayout)
        self.formWrapperLayout = QtWidgets.QVBoxLayout()
        self.formWrapperLayout.setContentsMargins(-1, 0, 0, 0)
        self.formWrapperLayout.setObjectName("formWrapperLayout")
        self.activeCategoryText = QtWidgets.QLabel(parent=self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setItalic(True)
        font.setUnderline(False)
        self.activeCategoryText.setFont(font)
        self.activeCategoryText.setStyleSheet("QLabel {\n"
"    color: #080a5d;\n"
"}")
        self.activeCategoryText.setWordWrap(True)
        self.activeCategoryText.setObjectName("activeCategoryText")
        self.formWrapperLayout.addWidget(self.activeCategoryText)
        self.setActiveButton = QtWidgets.QPushButton(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.setActiveButton.sizePolicy().hasHeightForWidth())
        self.setActiveButton.setSizePolicy(sizePolicy)
        self.setActiveButton.setMinimumSize(QtCore.QSize(250, 50))
        self.setActiveButton.setMaximumSize(QtCore.QSize(250, 50))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.setActiveButton.setFont(font)
        self.setActiveButton.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.setActiveButton.setObjectName("setActiveButton")
        self.formWrapperLayout.addWidget(self.setActiveButton)
        self.savedStatus = QtWidgets.QLabel(parent=self.centralwidget)
        self.savedStatus.setMaximumSize(QtCore.QSize(16777215, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setUnderline(False)
        self.savedStatus.setFont(font)
        self.savedStatus.setStyleSheet("QLabel {\n"
"    color: green;\n"
"}")
        self.savedStatus.setObjectName("savedStatus")
        self.formWrapperLayout.addWidget(self.savedStatus)
        self.formLayout = QtWidgets.QHBoxLayout()
        self.formLayout.setContentsMargins(0, -1, 0, 10)
        self.formLayout.setObjectName("formLayout")
        self.labelLayout = QtWidgets.QVBoxLayout()
        self.labelLayout.setContentsMargins(-1, -1, 0, 0)
        self.labelLayout.setSpacing(3)
        self.labelLayout.setObjectName("labelLayout")
        self.label_name = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_name.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_name.sizePolicy().hasHeightForWidth())
        self.label_name.setSizePolicy(sizePolicy)
        self.label_name.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_name.setFont(font)
        self.label_name.setObjectName("label_name")
        self.labelLayout.addWidget(self.label_name)
        self.label_autoStart = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_autoStart.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_autoStart.sizePolicy().hasHeightForWidth())
        self.label_autoStart.setSizePolicy(sizePolicy)
        self.label_autoStart.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_autoStart.setFont(font)
        self.label_autoStart.setObjectName("label_autoStart")
        self.labelLayout.addWidget(self.label_autoStart)
        self.label_splitName = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_splitName.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_splitName.setFont(font)
        self.label_splitName.setObjectName("label_splitName")
        self.labelLayout.addWidget(self.label_splitName)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Maximum)
        self.labelLayout.addItem(spacerItem)
        self.label_title = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_title.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_title.sizePolicy().hasHeightForWidth())
        self.label_title.setSizePolicy(sizePolicy)
        self.label_title.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_title.setFont(font)
        self.label_title.setObjectName("label_title")
        self.labelLayout.addWidget(self.label_title)
        self.label_outcome1 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_outcome1.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_outcome1.sizePolicy().hasHeightForWidth())
        self.label_outcome1.setSizePolicy(sizePolicy)
        self.label_outcome1.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_outcome1.setFont(font)
        self.label_outcome1.setObjectName("label_outcome1")
        self.labelLayout.addWidget(self.label_outcome1)
        self.label_outcome2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_outcome2.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_outcome2.sizePolicy().hasHeightForWidth())
        self.label_outcome2.setSizePolicy(sizePolicy)
        self.label_outcome2.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_outcome2.setFont(font)
        self.label_outcome2.setObjectName("label_outcome2")
        self.labelLayout.addWidget(self.label_outcome2)
        self.label_outcome3 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_outcome3.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_outcome3.sizePolicy().hasHeightForWidth())
        self.label_outcome3.setSizePolicy(sizePolicy)
        self.label_outcome3.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_outcome3.setFont(font)
        self.label_outcome3.setObjectName("label_outcome3")
        self.labelLayout.addWidget(self.label_outcome3)
        self.label_outcome4 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_outcome4.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_outcome4.sizePolicy().hasHeightForWidth())
        self.label_outcome4.setSizePolicy(sizePolicy)
        self.label_outcome4.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_outcome4.setFont(font)
        self.label_outcome4.setObjectName("label_outcome4")
        self.labelLayout.addWidget(self.label_outcome4)
        self.label_outcome5 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_outcome5.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_outcome5.sizePolicy().hasHeightForWidth())
        self.label_outcome5.setSizePolicy(sizePolicy)
        self.label_outcome5.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_outcome5.setFont(font)
        self.label_outcome5.setObjectName("label_outcome5")
        self.labelLayout.addWidget(self.label_outcome5)
        self.label_outcome6 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_outcome6.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_outcome6.sizePolicy().hasHeightForWidth())
        self.label_outcome6.setSizePolicy(sizePolicy)
        self.label_outcome6.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_outcome6.setFont(font)
        self.label_outcome6.setObjectName("label_outcome6")
        self.labelLayout.addWidget(self.label_outcome6)
        self.label_outcome7 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_outcome7.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_outcome7.sizePolicy().hasHeightForWidth())
        self.label_outcome7.setSizePolicy(sizePolicy)
        self.label_outcome7.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_outcome7.setFont(font)
        self.label_outcome7.setObjectName("label_outcome7")
        self.labelLayout.addWidget(self.label_outcome7)
        self.label_outcome8 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_outcome8.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_outcome8.sizePolicy().hasHeightForWidth())
        self.label_outcome8.setSizePolicy(sizePolicy)
        self.label_outcome8.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_outcome8.setFont(font)
        self.label_outcome8.setObjectName("label_outcome8")
        self.labelLayout.addWidget(self.label_outcome8)
        self.label_outcome9 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_outcome9.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_outcome9.sizePolicy().hasHeightForWidth())
        self.label_outcome9.setSizePolicy(sizePolicy)
        self.label_outcome9.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_outcome9.setFont(font)
        self.label_outcome9.setObjectName("label_outcome9")
        self.labelLayout.addWidget(self.label_outcome9)
        self.label_outcome10 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_outcome10.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_outcome10.sizePolicy().hasHeightForWidth())
        self.label_outcome10.setSizePolicy(sizePolicy)
        self.label_outcome10.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_outcome10.setFont(font)
        self.label_outcome10.setObjectName("label_outcome10")
        self.labelLayout.addWidget(self.label_outcome10)
        self.label_window = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_window.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_window.setFont(font)
        self.label_window.setObjectName("label_window")
        self.labelLayout.addWidget(self.label_window)
        self.formLayout.addLayout(self.labelLayout)
        self.fieldLayout = QtWidgets.QVBoxLayout()
        self.fieldLayout.setContentsMargins(-1, 0, 0, -1)
        self.fieldLayout.setSpacing(3)
        self.fieldLayout.setObjectName("fieldLayout")
        self.field_name = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.field_name.setMinimumSize(QtCore.QSize(200, 25))
        self.field_name.setMaximumSize(QtCore.QSize(250, 25))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.field_name.setFont(font)
        self.field_name.setStyleSheet("")
        self.field_name.setObjectName("field_name")
        self.fieldLayout.addWidget(self.field_name)
        self.field_autoStart = QtWidgets.QCheckBox(parent=self.centralwidget)
        self.field_autoStart.setMinimumSize(QtCore.QSize(15, 25))
        self.field_autoStart.setMaximumSize(QtCore.QSize(15, 25))
        self.field_autoStart.setSizeIncrement(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.field_autoStart.setFont(font)
        self.field_autoStart.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        self.field_autoStart.setStyleSheet("QCheckBox {\n"
"    outline: 0;\n"
"}")
        self.field_autoStart.setText("")
        self.field_autoStart.setIconSize(QtCore.QSize(0, 0))
        self.field_autoStart.setChecked(True)
        self.field_autoStart.setObjectName("field_autoStart")
        self.fieldLayout.addWidget(self.field_autoStart)
        self.field_splitName = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.field_splitName.setMinimumSize(QtCore.QSize(200, 25))
        self.field_splitName.setMaximumSize(QtCore.QSize(250, 25))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.field_splitName.setFont(font)
        self.field_splitName.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.IBeamCursor))
        self.field_splitName.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.field_splitName.setToolTip("")
        self.field_splitName.setStyleSheet("")
        self.field_splitName.setReadOnly(False)
        self.field_splitName.setObjectName("field_splitName")
        self.fieldLayout.addWidget(self.field_splitName)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Maximum)
        self.fieldLayout.addItem(spacerItem1)
        self.field_title = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.field_title.setMinimumSize(QtCore.QSize(200, 25))
        self.field_title.setMaximumSize(QtCore.QSize(250, 25))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.field_title.setFont(font)
        self.field_title.setObjectName("field_title")
        self.fieldLayout.addWidget(self.field_title)
        self.field_outcome1 = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.field_outcome1.setMinimumSize(QtCore.QSize(200, 25))
        self.field_outcome1.setMaximumSize(QtCore.QSize(250, 25))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.field_outcome1.setFont(font)
        self.field_outcome1.setObjectName("field_outcome1")
        self.fieldLayout.addWidget(self.field_outcome1)
        self.field_outcome2 = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.field_outcome2.setMinimumSize(QtCore.QSize(200, 25))
        self.field_outcome2.setMaximumSize(QtCore.QSize(250, 25))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.field_outcome2.setFont(font)
        self.field_outcome2.setStyleSheet("")
        self.field_outcome2.setObjectName("field_outcome2")
        self.fieldLayout.addWidget(self.field_outcome2)
        self.field_outcome3 = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.field_outcome3.setMinimumSize(QtCore.QSize(200, 25))
        self.field_outcome3.setMaximumSize(QtCore.QSize(250, 25))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.field_outcome3.setFont(font)
        self.field_outcome3.setObjectName("field_outcome3")
        self.fieldLayout.addWidget(self.field_outcome3)
        self.field_outcome4 = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.field_outcome4.setMinimumSize(QtCore.QSize(200, 25))
        self.field_outcome4.setMaximumSize(QtCore.QSize(250, 25))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.field_outcome4.setFont(font)
        self.field_outcome4.setObjectName("field_outcome4")
        self.fieldLayout.addWidget(self.field_outcome4)
        self.field_outcome5 = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.field_outcome5.setMinimumSize(QtCore.QSize(200, 25))
        self.field_outcome5.setMaximumSize(QtCore.QSize(250, 25))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.field_outcome5.setFont(font)
        self.field_outcome5.setObjectName("field_outcome5")
        self.fieldLayout.addWidget(self.field_outcome5)
        self.field_outcome6 = QtWidgets.QLineEdit(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.field_outcome6.sizePolicy().hasHeightForWidth())
        self.field_outcome6.setSizePolicy(sizePolicy)
        self.field_outcome6.setMinimumSize(QtCore.QSize(200, 25))
        self.field_outcome6.setMaximumSize(QtCore.QSize(250, 25))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.field_outcome6.setFont(font)
        self.field_outcome6.setObjectName("field_outcome6")
        self.fieldLayout.addWidget(self.field_outcome6)
        self.field_outcome7 = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.field_outcome7.setMinimumSize(QtCore.QSize(200, 25))
        self.field_outcome7.setMaximumSize(QtCore.QSize(250, 25))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.field_outcome7.setFont(font)
        self.field_outcome7.setObjectName("field_outcome7")
        self.fieldLayout.addWidget(self.field_outcome7)
        self.field_outcome8 = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.field_outcome8.setMinimumSize(QtCore.QSize(200, 25))
        self.field_outcome8.setMaximumSize(QtCore.QSize(250, 25))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.field_outcome8.setFont(font)
        self.field_outcome8.setObjectName("field_outcome8")
        self.fieldLayout.addWidget(self.field_outcome8)
        self.field_outcome9 = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.field_outcome9.setMinimumSize(QtCore.QSize(200, 25))
        self.field_outcome9.setMaximumSize(QtCore.QSize(250, 25))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.field_outcome9.setFont(font)
        self.field_outcome9.setObjectName("field_outcome9")
        self.fieldLayout.addWidget(self.field_outcome9)
        self.field_outcome10 = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.field_outcome10.setMinimumSize(QtCore.QSize(200, 25))
        self.field_outcome10.setMaximumSize(QtCore.QSize(250, 25))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.field_outcome10.setFont(font)
        self.field_outcome10.setObjectName("field_outcome10")
        self.fieldLayout.addWidget(self.field_outcome10)
        self.field_window = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.field_window.setMaximumSize(QtCore.QSize(250, 25))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.field_window.setFont(font)
        self.field_window.setObjectName("field_window")
        self.fieldLayout.addWidget(self.field_window)
        self.formLayout.addLayout(self.fieldLayout)
        self.formWrapperLayout.addLayout(self.formLayout)
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetDefaultConstraint)
        self.buttonLayout.setContentsMargins(-1, -1, 120, -1)
        self.buttonLayout.setSpacing(40)
        self.buttonLayout.setObjectName("buttonLayout")
        self.saveButton = QtWidgets.QPushButton(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.saveButton.sizePolicy().hasHeightForWidth())
        self.saveButton.setSizePolicy(sizePolicy)
        self.saveButton.setMinimumSize(QtCore.QSize(90, 0))
        self.saveButton.setMaximumSize(QtCore.QSize(130, 50))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.saveButton.setFont(font)
        self.saveButton.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.saveButton.setObjectName("saveButton")
        self.buttonLayout.addWidget(self.saveButton)
        self.deleteButton = QtWidgets.QPushButton(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deleteButton.sizePolicy().hasHeightForWidth())
        self.deleteButton.setSizePolicy(sizePolicy)
        self.deleteButton.setMinimumSize(QtCore.QSize(80, 50))
        self.deleteButton.setMaximumSize(QtCore.QSize(80, 50))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.deleteButton.setFont(font)
        self.deleteButton.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.deleteButton.setObjectName("deleteButton")
        self.buttonLayout.addWidget(self.deleteButton)
        self.formWrapperLayout.addLayout(self.buttonLayout)
        self.mainLayout.addLayout(self.formWrapperLayout)
        self.gridLayout.addLayout(self.mainLayout, 0, 2, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 900, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(parent=self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.actionFile = QtGui.QAction(parent=MainWindow)
        self.actionFile.setObjectName("actionFile")
        self.actionOpen = QtGui.QAction(parent=MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.menuFile.addAction(self.actionOpen)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.categoriesLabel.setText(_translate("MainWindow", "Categories"))
        self.categoryList.setSortingEnabled(False)
        self.removeCatButton.setText(_translate("MainWindow", "Remove Category"))
        self.splitsLabel.setText(_translate("MainWindow", "Splits"))
        self.activeCategoryText.setText(_translate("MainWindow", "Active Category: "))
        self.setActiveButton.setText(_translate("MainWindow", "Set selected category as active"))
        self.savedStatus.setText(_translate("MainWindow", "Status: Saved"))
        self.label_name.setToolTip(_translate("MainWindow", "<html><head/><body><p>This is the name used to start a prediction via Twitch chat.</p><p>This name must be unique across all predictions of a certain category.</p></body></html>"))
        self.label_name.setText(_translate("MainWindow", "Name *"))
        self.label_autoStart.setText(_translate("MainWindow", "Auto start"))
        self.label_splitName.setText(_translate("MainWindow", "Split name"))
        self.label_title.setText(_translate("MainWindow", "Title *"))
        self.label_outcome1.setText(_translate("MainWindow", "Outcome 1 *"))
        self.label_outcome2.setText(_translate("MainWindow", "Outcome 2 *"))
        self.label_outcome3.setText(_translate("MainWindow", "Outcome 3"))
        self.label_outcome4.setText(_translate("MainWindow", "Outcome 4"))
        self.label_outcome5.setText(_translate("MainWindow", "Outcome 5"))
        self.label_outcome6.setText(_translate("MainWindow", "Outcome 6"))
        self.label_outcome7.setText(_translate("MainWindow", "Outcome 7"))
        self.label_outcome8.setText(_translate("MainWindow", "Outcome 8"))
        self.label_outcome9.setText(_translate("MainWindow", "Outcome 9"))
        self.label_outcome10.setText(_translate("MainWindow", "Outcome 10"))
        self.label_window.setText(_translate("MainWindow", "Window (in seconds) *"))
        self.saveButton.setText(_translate("MainWindow", "Save Prediction"))
        self.deleteButton.setText(_translate("MainWindow", "Delete"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionFile.setText(_translate("MainWindow", "File"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))