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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QSizePolicy, QSpacerItem,
    QTableView, QToolButton, QVBoxLayout, QWidget)

class Ui_FoodSearchWidget(object):
    def setupUi(self, FoodSearchWidget):
        if not FoodSearchWidget.objectName():
            FoodSearchWidget.setObjectName(u"FoodSearchWidget")
        FoodSearchWidget.resize(537, 392)
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

        self.foodTableView = QTableView(self.frame)
        self.foodTableView.setObjectName(u"foodTableView")

        self.verticalLayout_2.addWidget(self.foodTableView)


        self.verticalLayout.addWidget(self.frame)


        self.retranslateUi(FoodSearchWidget)

        QMetaObject.connectSlotsByName(FoodSearchWidget)
    # setupUi

    def retranslateUi(self, FoodSearchWidget):
        FoodSearchWidget.setWindowTitle(QCoreApplication.translate("FoodSearchWidget", u"Form", None))
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
        self.exportFoodButton.setText(QCoreApplication.translate("FoodSearchWidget", u"...", None))
#if QT_CONFIG(tooltip)
        self.deleteFoodButton.setToolTip(QCoreApplication.translate("FoodSearchWidget", u"Delete Food", None))
#endif // QT_CONFIG(tooltip)
        self.deleteFoodButton.setText(QCoreApplication.translate("FoodSearchWidget", u"...", None))
        self.label.setText(QCoreApplication.translate("FoodSearchWidget", u"Search: ", None))
    # retranslateUi

