# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'foodSearchWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QAbstractSpinBox, QApplication, QComboBox,
    QFrame, QGridLayout, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QStackedWidget, QTableView,
    QToolButton, QVBoxLayout, QWidget)

class Ui_FoodSearchWidget(object):
    def setupUi(self, FoodSearchWidget):
        if not FoodSearchWidget.objectName():
            FoodSearchWidget.setObjectName(u"FoodSearchWidget")
        FoodSearchWidget.resize(686, 607)
        self.verticalLayout = QVBoxLayout(FoodSearchWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.addFoodButton = QToolButton(FoodSearchWidget)
        self.addFoodButton.setObjectName(u"addFoodButton")

        self.horizontalLayout.addWidget(self.addFoodButton)

        self.importFoodButton = QToolButton(FoodSearchWidget)
        self.importFoodButton.setObjectName(u"importFoodButton")

        self.horizontalLayout.addWidget(self.importFoodButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.editFoodButton = QToolButton(FoodSearchWidget)
        self.editFoodButton.setObjectName(u"editFoodButton")

        self.horizontalLayout.addWidget(self.editFoodButton)

        self.dupFoodButton = QToolButton(FoodSearchWidget)
        self.dupFoodButton.setObjectName(u"dupFoodButton")

        self.horizontalLayout.addWidget(self.dupFoodButton)

        self.exportFoodButton = QToolButton(FoodSearchWidget)
        self.exportFoodButton.setObjectName(u"exportFoodButton")

        self.horizontalLayout.addWidget(self.exportFoodButton)

        self.deleteFoodButton = QToolButton(FoodSearchWidget)
        self.deleteFoodButton.setObjectName(u"deleteFoodButton")

        self.horizontalLayout.addWidget(self.deleteFoodButton)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.frame = QFrame(FoodSearchWidget)
        self.frame.setObjectName(u"frame")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(4)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label, 0, Qt.AlignmentFlag.AlignRight)

        self.searchLineEdit = QLineEdit(self.frame)
        self.searchLineEdit.setObjectName(u"searchLineEdit")

        self.horizontalLayout_2.addWidget(self.searchLineEdit)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.sourcesWidget = QWidget(self.frame)
        self.sourcesWidget.setObjectName(u"sourcesWidget")
        self.horizontalLayout_3 = QHBoxLayout(self.sourcesWidget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")

        self.verticalLayout_2.addWidget(self.sourcesWidget)

        self.foodTableView = QTableView(self.frame)
        self.foodTableView.setObjectName(u"foodTableView")
        self.foodTableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.foodTableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.foodTableView.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.foodTableView.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.foodTableView.horizontalHeader().setVisible(True)
        self.foodTableView.verticalHeader().setVisible(False)

        self.verticalLayout_2.addWidget(self.foodTableView)


        self.verticalLayout.addWidget(self.frame)

        self.foodDetailStack = QStackedWidget(FoodSearchWidget)
        self.foodDetailStack.setObjectName(u"foodDetailStack")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.horizontalLayout_4 = QHBoxLayout(self.page)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_4 = QLabel(self.page)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_4.addWidget(self.label_4, 0, Qt.AlignmentFlag.AlignHCenter)

        self.foodDetailStack.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.verticalLayout_3 = QVBoxLayout(self.page_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.foodNameLabel = QLabel(self.page_2)
        self.foodNameLabel.setObjectName(u"foodNameLabel")
        self.foodNameLabel.setTextFormat(Qt.TextFormat.PlainText)
        self.foodNameLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_3.addWidget(self.foodNameLabel)

        self.frame_2 = QFrame(self.page_2)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout = QGridLayout(self.frame_2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.carbsLabel = QLabel(self.frame_2)
        self.carbsLabel.setObjectName(u"carbsLabel")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.carbsLabel.sizePolicy().hasHeightForWidth())
        self.carbsLabel.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.carbsLabel, 1, 4, 1, 1)

        self.label_3 = QLabel(self.frame_2)
        self.label_3.setObjectName(u"label_3")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.label_3, 1, 1, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.fatLabel = QLabel(self.frame_2)
        self.fatLabel.setObjectName(u"fatLabel")
        sizePolicy1.setHeightForWidth(self.fatLabel.sizePolicy().hasHeightForWidth())
        self.fatLabel.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.fatLabel, 1, 6, 1, 1)

        self.label_16 = QLabel(self.frame_2)
        self.label_16.setObjectName(u"label_16")
        sizePolicy2.setHeightForWidth(self.label_16.sizePolicy().hasHeightForWidth())
        self.label_16.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.label_16, 2, 3, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.label_7 = QLabel(self.frame_2)
        self.label_7.setObjectName(u"label_7")
        sizePolicy2.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.label_7, 1, 3, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.cholLabel = QLabel(self.frame_2)
        self.cholLabel.setObjectName(u"cholLabel")
        sizePolicy1.setHeightForWidth(self.cholLabel.sizePolicy().hasHeightForWidth())
        self.cholLabel.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.cholLabel, 2, 4, 1, 1)

        self.label_18 = QLabel(self.frame_2)
        self.label_18.setObjectName(u"label_18")
        sizePolicy2.setHeightForWidth(self.label_18.sizePolicy().hasHeightForWidth())
        self.label_18.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.label_18, 2, 5, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.satFatLabel = QLabel(self.frame_2)
        self.satFatLabel.setObjectName(u"satFatLabel")
        sizePolicy1.setHeightForWidth(self.satFatLabel.sizePolicy().hasHeightForWidth())
        self.satFatLabel.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.satFatLabel, 2, 6, 1, 1)

        self.proteinLabel = QLabel(self.frame_2)
        self.proteinLabel.setObjectName(u"proteinLabel")
        sizePolicy1.setHeightForWidth(self.proteinLabel.sizePolicy().hasHeightForWidth())
        self.proteinLabel.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.proteinLabel, 1, 2, 1, 1)

        self.energyLabel = QLabel(self.frame_2)
        self.energyLabel.setObjectName(u"energyLabel")
        sizePolicy1.setHeightForWidth(self.energyLabel.sizePolicy().hasHeightForWidth())
        self.energyLabel.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.energyLabel, 0, 2, 1, 1)

        self.label_14 = QLabel(self.frame_2)
        self.label_14.setObjectName(u"label_14")
        sizePolicy2.setHeightForWidth(self.label_14.sizePolicy().hasHeightForWidth())
        self.label_14.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.label_14, 2, 1, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.label_6 = QLabel(self.frame_2)
        self.label_6.setObjectName(u"label_6")
        sizePolicy2.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.label_6, 0, 3, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.fiberLabel = QLabel(self.frame_2)
        self.fiberLabel.setObjectName(u"fiberLabel")
        sizePolicy1.setHeightForWidth(self.fiberLabel.sizePolicy().hasHeightForWidth())
        self.fiberLabel.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.fiberLabel, 0, 6, 1, 1)

        self.waterLabel = QLabel(self.frame_2)
        self.waterLabel.setObjectName(u"waterLabel")
        sizePolicy1.setHeightForWidth(self.waterLabel.sizePolicy().hasHeightForWidth())
        self.waterLabel.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.waterLabel, 0, 4, 1, 1)

        self.label_10 = QLabel(self.frame_2)
        self.label_10.setObjectName(u"label_10")
        sizePolicy2.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.label_10, 0, 5, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.label_2 = QLabel(self.frame_2)
        self.label_2.setObjectName(u"label_2")
        sizePolicy2.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.sugarLabel = QLabel(self.frame_2)
        self.sugarLabel.setObjectName(u"sugarLabel")
        sizePolicy1.setHeightForWidth(self.sugarLabel.sizePolicy().hasHeightForWidth())
        self.sugarLabel.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.sugarLabel, 2, 2, 1, 1)

        self.label_12 = QLabel(self.frame_2)
        self.label_12.setObjectName(u"label_12")
        sizePolicy2.setHeightForWidth(self.label_12.sizePolicy().hasHeightForWidth())
        self.label_12.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.label_12, 1, 5, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.horizontalSpacer_2 = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 0, 0, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_3, 1, 7, 1, 1)


        self.verticalLayout_3.addWidget(self.frame_2)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.measureSpinBox = QSpinBox(self.page_2)
        self.measureSpinBox.setObjectName(u"measureSpinBox")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.measureSpinBox.sizePolicy().hasHeightForWidth())
        self.measureSpinBox.setSizePolicy(sizePolicy3)
        self.measureSpinBox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.measureSpinBox.setMaximum(1000000025)

        self.horizontalLayout_5.addWidget(self.measureSpinBox)

        self.measureComboBox = QComboBox(self.page_2)
        self.measureComboBox.setObjectName(u"measureComboBox")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.measureComboBox.sizePolicy().hasHeightForWidth())
        self.measureComboBox.setSizePolicy(sizePolicy4)

        self.horizontalLayout_5.addWidget(self.measureComboBox)

        self.addServingButton = QPushButton(self.page_2)
        self.addServingButton.setObjectName(u"addServingButton")

        self.horizontalLayout_5.addWidget(self.addServingButton)


        self.verticalLayout_3.addLayout(self.horizontalLayout_5)

        self.foodDetailStack.addWidget(self.page_2)

        self.verticalLayout.addWidget(self.foodDetailStack)


        self.retranslateUi(FoodSearchWidget)

        QMetaObject.connectSlotsByName(FoodSearchWidget)
    # setupUi

    def retranslateUi(self, FoodSearchWidget):
        FoodSearchWidget.setWindowTitle(QCoreApplication.translate("FoodSearchWidget", u"FoodSearchWidget", None))
#if QT_CONFIG(tooltip)
        self.addFoodButton.setToolTip(QCoreApplication.translate("FoodSearchWidget", u"Create New Food", None))
#endif // QT_CONFIG(tooltip)
        self.addFoodButton.setText("")
#if QT_CONFIG(tooltip)
        self.importFoodButton.setToolTip(QCoreApplication.translate("FoodSearchWidget", u"Import Food", None))
#endif // QT_CONFIG(tooltip)
        self.importFoodButton.setText("")
#if QT_CONFIG(tooltip)
        self.editFoodButton.setToolTip(QCoreApplication.translate("FoodSearchWidget", u"Edit Food", None))
#endif // QT_CONFIG(tooltip)
        self.editFoodButton.setText(QCoreApplication.translate("FoodSearchWidget", u"...", None))
#if QT_CONFIG(tooltip)
        self.dupFoodButton.setToolTip(QCoreApplication.translate("FoodSearchWidget", u"Duplicate Food", None))
#endif // QT_CONFIG(tooltip)
        self.dupFoodButton.setText(QCoreApplication.translate("FoodSearchWidget", u"...", None))
#if QT_CONFIG(tooltip)
        self.exportFoodButton.setToolTip(QCoreApplication.translate("FoodSearchWidget", u"Duplicate Food", None))
#endif // QT_CONFIG(tooltip)
        self.exportFoodButton.setText(QCoreApplication.translate("FoodSearchWidget", u"...", None))
#if QT_CONFIG(tooltip)
        self.deleteFoodButton.setToolTip(QCoreApplication.translate("FoodSearchWidget", u"Delete Food", None))
#endif // QT_CONFIG(tooltip)
        self.deleteFoodButton.setText(QCoreApplication.translate("FoodSearchWidget", u"...", None))
        self.label.setText(QCoreApplication.translate("FoodSearchWidget", u"Search: ", None))
        self.label_4.setText(QCoreApplication.translate("FoodSearchWidget", u"No Food Selected", None))
        self.foodNameLabel.setText("")
        self.carbsLabel.setText("")
        self.label_3.setText(QCoreApplication.translate("FoodSearchWidget", u"Protein:", None))
        self.fatLabel.setText("")
        self.label_16.setText(QCoreApplication.translate("FoodSearchWidget", u"Cholesterol:", None))
        self.label_7.setText(QCoreApplication.translate("FoodSearchWidget", u"Carbs:", None))
        self.cholLabel.setText("")
        self.label_18.setText(QCoreApplication.translate("FoodSearchWidget", u"Saturated Fat:", None))
        self.satFatLabel.setText("")
        self.proteinLabel.setText("")
        self.energyLabel.setText("")
        self.label_14.setText(QCoreApplication.translate("FoodSearchWidget", u"Sugar:", None))
        self.label_6.setText(QCoreApplication.translate("FoodSearchWidget", u"Water:", None))
        self.fiberLabel.setText("")
        self.waterLabel.setText("")
        self.label_10.setText(QCoreApplication.translate("FoodSearchWidget", u"Fiber:", None))
        self.label_2.setText(QCoreApplication.translate("FoodSearchWidget", u"Energy:", None))
        self.sugarLabel.setText("")
        self.label_12.setText(QCoreApplication.translate("FoodSearchWidget", u"Fat:", None))
        self.addServingButton.setText(QCoreApplication.translate("FoodSearchWidget", u"Add", None))
    # retranslateUi

