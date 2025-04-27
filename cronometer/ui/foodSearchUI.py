"""
View for searching all loaded food databases for a particular food.
"""
import re

from typing import Any

from pydantic import BaseModel
from Qt import QtCore
from Qt import QtWidgets

from cronometer.core.foodManager import FoodManager
from cronometer.foods.food import FoodProxy
from cronometer.foods.food import FoodSource
from cronometer.ui.ui_foodSearchWidget import Ui_FoodSearchWidget
from cronometer.util.datautils import asPercentage

COL_DESC = "Description"
COL_PERC = "%"

COLUMNS = [COL_DESC, COL_PERC]


class _TableData(BaseModel):
    """
    Holds the table model data.
    """
    proxy: FoodProxy
    consumption: float
    sortName: str
    consumptionStr: str


class FoodSearchWidget(QtWidgets.QWidget, Ui_FoodSearchWidget):
    """
    Extenstion of the generated UI code with an initialize method to set
    everything up.
    """
    def initialize(self,
                   manager: FoodManager,
                   consumption: dict[tuple[FoodSource, int], int]):
        """
        Setup the ui to be usable.

        Most call this before trying to use the widget.
        """
        self.setupUi(self)
        self.__manager = manager
        self.__model = LoadedFoodModel(manager, consumption)

        self.foodTableView.setSortingEnabled(True)
        self.foodTableView.setModel(self.__model)
        self.foodTableView.sortByColumn(1, QtCore.Qt.DescendingOrder)
        self.foodTableView.resizeColumnsToContents()
        self.searchLineEdit.textChanged.connect(self.__startTimer)
        self.__timer = QtCore.QTimer()
        self.__timer.setInterval(80)
        self.__timer.timeout.connect(self.__filterTable)

    def __startTimer(self, _=None):
        """
        Start the timer that will cause the table to filter when it
        times out
        """
        self.__timer.start()

    def __filterTable(self):
        """
        Update the table filter when the user types something
        """
        self.__timer.stop()
        self.__model.setFilterSting(self.searchLineEdit.text())


class LoadedFoodModel(QtCore.QAbstractItemModel):
    """
    Takes the Food Manager and serving info and creates a model
    for viewing all of the loaded foods.
    """
    def __init__(self,
                 manager: FoodManager,
                 consumption: dict[tuple[FoodSource, int], int]):
        """
        Create a new food model.
        """
        super().__init__()
        self.__manager = manager
        self.__consumption = consumption
        self.__data = list[_TableData]()
        self.__filteredData = list[_TableData]()

        self.__filterString: str = ""

        self.__sortColumn = -1
        self.__sortOrder = QtCore.Qt.AscendingOrder

        # If empty, use all loaded sources. Otherwise only use the sources
        # that are in an intersection of this set and the loaded sources.
        self.__sourcesToUse = set[FoodSource]()

        self.__updateModelData()

        self.__manager.sourceRemoved.connect(self.__updateModelData)
        self.__manager.sourceAdded.connect(self.__updateModelData)

    def __updateModelData(self):
        """
        Update the internal model data structures as a result of a source being
        added or removed
        """
        self.beginResetModel()

        if self.__sourcesToUse:
            sources = self.__sourcesToUse.intersection(self.__manager.sources())
        else:
            sources = self.__manager.sources()

        self.__data.clear()
        for source in sources:
            for proxy in self.__manager.getFoodProxies(source):
                td = _TableData(proxy=proxy,
                                consumption=0.0,
                                sortName=proxy.name.lower(),
                                consumptionStr="")
                self.__data.append(td)
        self.__setConsumption()
        self.__filter()
        self.__sort()
        self.endResetModel()

    def setConsumption(self, consumption: dict[tuple[FoodSource, int], int]):
        """
        Update the consumption data the model is using.
        """
        self.beginResetModel()
        self.__consumption = consumption
        self.__setConsumption()
        self.endResetModel()

    def __setConsumption(self):
        """
        Helper method that updates the consumption data in all the _TableData
        instances.

        Does not call begin/endResetModel so make sure it is called in a
        context where that is being done
        """
        most = max(self.__consumption.values())
        for td in self.__data:
            times = self.__consumption.get((td.proxy.foodSource, td.proxy.sourceUID),
                                           0.0)
            td.consumption = times / most
            td.consumptionStr = asPercentage(td.consumption)

    def index(self, row: int, column: int,
              parent: QtCore.QModelIndex) -> QtCore.QModelIndex:
        """
        Create a new index.
        """
        return self.createIndex(row, column, None)

    def rowCount(self, parent: QtCore.QModelIndex) -> int:
        """
        Number of rows in the table.
        """
        return len(self.__filteredData)

    def columnCount(self, parent: QtCore.QModelIndex) -> int:
        return len(COLUMNS)

    def parent(self, index: QtCore.QModelIndex) -> QtCore.QModelIndex:
        return QtCore.QModelIndex()

    def headerData(self,
                   section: int,
                   orientation: QtCore.Qt.Orientation,
                   role: QtCore.Qt.ItemDataRole = QtCore.Qt.DisplayRole) -> Any:
        """
        Return the header data for each column in the table
        """
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return COLUMNS[section]

    def sort(self,
             column: int,
             order: QtCore.Qt.SortOrder = QtCore.Qt.AscendingOrder):
        """
        Sort the model by the given column.

        Does not call begin/endResetModel so make sure it is called in a
        context where that is being done
        """
        self.__sortColumn = column
        self.__sortOrder = order

        self.beginResetModel()
        self.__sort()
        self.endResetModel()

    def setFilterSting(self, filterString: str):
        """
        Set the string that will be used to filter the model
        """
        fstring = filterString.strip().lower()
        refine = fstring.startswith(self.__filterString)
        self.__filterString = fstring
        self.beginResetModel()
        self.__filter(refine)
        self.__sort()
        self.endResetModel()

    def __filter(self, refine: bool = False):
        """
        Filter the data.

        If refine is true, then the filter will start with the results of
        the last filter. This should make filtering big data sets faster.

        Does not call begin/endResetModel so make sure it is called in a
        context where that is being done.
        """
        terms = self.__filterString.split()

        if not terms:
            self.__filteredData = list(self.__data)
        else:

            # searchTerm = r"(?=.*{})"
            # regexTerm = ".*{}.*".format("".join((searchTerm.format(t) for t in terms)))
            # regex = re.compile(regexTerm)

            # self.__filteredData = [td for td in self.__data if regex.match(td.sortName)]
            start = self.__filteredData if refine else self.__data
            self.__filteredData = [td for td in start
                                   if all(t in td.sortName for t in terms)]

    def __sort(self):
        """
        Sort the currently visible data according to the current sort params
        """
        # no sorting
        if self.__sortColumn == -1:
            return
        col = COLUMNS[self.__sortColumn]

        def sortVal(td: _TableData):
            if col == COL_DESC:
                return td.sortName
            elif col == COL_PERC:
                return td.consumption
            return ""

        self.__filteredData.sort(
            key=lambda x: sortVal(x),
            reverse=self.__sortOrder == QtCore.Qt.DescendingOrder)

    def data(self,
             index: QtCore.QModelIndex,
             role: QtCore.Qt.ItemDataRole = QtCore.Qt.DisplayRole) -> Any:
        """
        Return the data for each table cell.
        """
        if not index.isValid():
            return None

        col = COLUMNS[index.column()]
        td = self.__filteredData[index.row()]

        if role == QtCore.Qt.DisplayRole:
            if col == COL_DESC:
                return td.proxy.name
            elif col == COL_PERC:
                return td.consumptionStr
