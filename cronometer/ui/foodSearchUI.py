"""
View for searching all loaded food databases for a particular food.
"""
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

SORT_ROLE = QtCore.Qt.UserRole


class _TableData(BaseModel):
    """
    Class
    """
    proxy: FoodProxy
    consumption: float
    sortName: str
    comsumptionStr: str


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
        print(self.__model.rowCount(QtCore.QModelIndex()))
        self.__sortModel = QtCore.QSortFilterProxyModel()
        self.__sortModel.setSourceModel(self.__model)
        # Default to sorting by comsumption
        self.__sortModel.setSortRole(SORT_ROLE)
        self.__sortModel.sort(1, QtCore.Qt.DescendingOrder)

        self.foodTableView.setSortingEnabled(True)
        self.foodTableView.setModel(self.__sortModel)
        self.foodTableView.resizeColumnsToContents()
        self.searchLineEdit.textChanged.connect(self.__filterTable)

    def __filterTable(self, text):
        """
        Update the table filter when the user types something
        """
        # terms = text.split()

        # searchTerm = r"(?=.*{})"
        # regexTerm = ".*{}.*".format("".join((searchTerm.format(t) for t in terms)))

        # regex = QtCore.QRegularExpression(
        #     regexTerm, QtCore.QRegularExpression.CaseInsensitiveOption)
        # self.__sortModel.setFilterRegularExpression(regex)

        timer = QtCore.QElapsedTimer()
        timer.start()
        self.foodTableView.setVisible(False)
        self.__sortModel.setFilterFixedString(text)
        self.foodTableView.setVisible(True)
        print(f"Filter took {timer.elapsed()} ms")



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
        self.__consumption = dict[tuple[FoodSource, int], float]()
        self.setComsumption(consumption)

        # If empty, use all loaded sources. Otherwise only use the sources
        # that are in an intersection of this set and the loaded sources.
        self.__sourcesToUse = set[FoodSource]()

        self.__offsets = dict[FoodSource, tuple[int, int]]()
        self.__foodNames = dict[FoodSource, list[str]]()
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

        self.__offsets.clear()
        offset = 0
        for source in sources:
            foodCount = self.__manager.getFoodCount(source)
            self.__offsets[source] = (offset, offset + foodCount - 1)
            offset += foodCount
        self.__foodNames = {
            s : self.__manager.getFoodNames(s) for s in self.__manager.sources()}
        self.endResetModel()

    def setComsumption(self, consumption: dict[tuple[FoodSource, int], int]):
        """
        Update the consumption data the model is using.
        """
        self.beginResetModel()
        most = max(consumption.values())
        self.__consumption = dict()
        for ((source, uid), times) in consumption.items():
            self.__consumption[(source,
                                self.__manager.getFoodIndex(source,
                                                            uid))] = times / most
        self.endResetModel()

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
        return self.__manager.getFoodCount()

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



    def data(self,
             index: QtCore.QModelIndex,
             role: QtCore.Qt.ItemDataRole = QtCore.Qt.DisplayRole) -> Any:
        """
        Return the data for each table cell.
        """
        if not index.isValid():
            return None

        col = COLUMNS[index.column()]

        if role == QtCore.Qt.DisplayRole:
            if col == COL_DESC:
                return self.__getFoodName(index.row())
            elif col == COL_PERC:
                source, idx = self.__getSourceAndIndex(index.row())
                return asPercentage(self.__consumption.get((source, idx), 0.0))
                return 0.0
        if role == SORT_ROLE:
            if col == COL_DESC:
                return self.__getFoodName(index.row()).lower()
            elif col == COL_PERC:
                source, idx = self.__getSourceAndIndex(index.row())
                return self.__consumption.get((source, idx), 0.0)

    def __getSourceAndIndex(self, row) -> tuple[FoodSource, int]:
        """
        From a given row number, get the food source and index for
        the food in that row.
        """
        for source, offsets in self.__offsets.items():
            if row >= offsets[0] and row <= offsets[1]:
                index = row - offsets[0]
                return (source, index)
        raise IndexError(f"No food in row {row}")

    def __getFoodName(self, row) -> str:
        """
        Get the food from the given row.
        """
        source, index = self.__getSourceAndIndex(row)
        return self.__foodNames[source][index]
