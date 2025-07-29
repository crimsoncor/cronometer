"""
The main part of the cronometer UI.
"""
import os

from datetime import date as dtdate
from datetime import timedelta
from typing import Optional

from Qt import QtCompat
from Qt import QtWidgets

from cronometer.core.foodManager import FoodManager
from cronometer.foods.foodHistory import FoodHistoryDB
from cronometer.qt.style import setupIcon
from cronometer.ui.servingsUI import ServingModel
from cronometer.ui.ui_servingsPanel import Ui_ServingsPanel
from cronometer.user.user import User
from cronometer.user.userDay import UserDay

THIS_DIR = os.path.abspath(os.path.dirname(__file__))


class ServingsPanel(Ui_ServingsPanel, QtWidgets.QWidget):
    """
    Extension of the generated UI code with an initialize method to set
    everything up.
    """
    def __init__(self, parent=None):
        """
        Create a new widget.
        """
        super().__init__(parent)
        QtCompat.loadUi(os.path.join(THIS_DIR, "servingsPanel.ui"), self)

    def initialize(self, manager: FoodManager):
        """
        Setup the ui to be usable.

        Must call this before trying to use the widget.
        """
        self.__manager = manager
        self.__servingModel = ServingModel()
        self.__foodDB: Optional[FoodHistoryDB] = None
        self.__user: Optional[User] = None
        self.__date: dtdate = dtdate.today()

        self.servingTreeView.setModel(self.__servingModel)
        header = self.servingTreeView.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Interactive)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)

        setupIcon(self.todayButton, "Today.svg")
        setupIcon(self.backButton, "Back.svg")
        setupIcon(self.forwardButton, "Forward.svg")
        setupIcon(self.copyToDayButton, "Copy.svg")
        setupIcon(self.addServingButton, "Add.svg")
        setupIcon(self.deleteServingButton, "Delete.svg")

        self.backButton.clicked.connect(self.__handleBack)
        self.forwardButton.clicked.connect(self.__handleForward)

    def setUser(self, user: User, foodDB: FoodHistoryDB):
        """
        Set the current user whose food is going to be shown in the UI.
        """
        self.__user = user
        self.__foodDB = foodDB

        self.__refresh()

    def __clear(self):
        """
        Clear all entries in the UI.
        """
        self.__servingModel.setUserDay(None)

    def __refresh(self):
        """
        Update the entire UI with the current state.
        """
        self.__clear()

        self.dateButton.setText(self.__date.strftime("%b %d, %Y"))

        if self.__foodDB:
            userDay = UserDay(self.__manager, self.__foodDB.getDay(self.__date))
            self.__servingModel.setUserDay(userDay)
            self.servingTreeView.resizeColumnToContents(0)
            self.servingTreeView.resizeColumnToContents(2)

    def __handleBack(self, _=None):
        """
        Handle the user pressing the date back button
        """
        self.__date = self.__date - timedelta(days=1)
        self.__refresh()

    def __handleForward(self, _=None):
        """
        Handle the user pressing the date forward button
        """
        self.__date = self.__date + timedelta(days=1)
        self.__refresh()
