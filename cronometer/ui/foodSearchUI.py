"""
View for searching all loaded food databases for a particular food.
"""
import os

from datetime import date
from typing import Any
from typing import Optional

from pydantic import BaseModel
from Qt import QtCompat
from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets

from cronometer.core.foodManager import FoodManager
from cronometer.foods.food import Food
from cronometer.foods.food import FoodProxy
from cronometer.foods.food import FoodSource
from cronometer.qt import qtutils
from cronometer.qt.style import setupIcon
from cronometer.ui.ui_foodSearchWidget import Ui_FoodSearchWidget
from cronometer.util.datautils import asPercentage
from cronometer.util.datautils import formatAmount

COL_SOURCE = "Source"
COL_DESC = "Description"
COL_DATE = "Date"
COL_PERC = "%"

COLUMNS = [COL_SOURCE, COL_DESC, COL_DATE, COL_PERC]

THIS_DIR = os.path.abspath(os.path.dirname(__file__))


class _TableData(BaseModel):
    """
    Holds the table model data.
    """
    proxy: FoodProxy
    consumption: float
    sortName: str
    consumptionStr: str


#FIXME Decide on generated code vs UI file loading.
class FoodSearchWidget(Ui_FoodSearchWidget, QtWidgets.QWidget):
    """
    Extension of the generated UI code with an initialize method to set
    everything up.
    """
    def __init__(self, parent=None):
        """
        Create a new widget.
        """
        super().__init__(parent)
        QtCompat.loadUi(os.path.join(THIS_DIR, "foodSearchWidget.ui"), self)

        self.__currentFood: Optional[Food] = None

    def initialize(self,
                   manager: FoodManager,
                   consumption: dict[tuple[FoodSource, int], int]):
        """
        Setup the ui to be usable.

        Must call this before trying to use the widget.
        """
        self.__manager = manager
        self.__model = LoadedFoodModel(manager, consumption)

        self.foodTableView.setSortingEnabled(True)
        self.foodTableView.setModel(self.__model)
        self.foodTableView.sortByColumn(COLUMNS.index(COL_PERC),
                                        QtCore.Qt.DescendingOrder)
        self.foodTableView.doubleClicked.connect(self.__foodDoubleClicked)
        header = self.foodTableView.horizontalHeader()
        header.setSectionResizeMode(COLUMNS.index(COL_SOURCE),
                                    QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(COLUMNS.index(COL_DATE),
                                    QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(COLUMNS.index(COL_DESC),
                                    QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(COLUMNS.index(COL_PERC),
                                    QtWidgets.QHeaderView.ResizeToContents)
        selectionModel = self.foodTableView.selectionModel()
        selectionModel.selectionChanged.connect(self.__foodSelected)
        self.searchLineEdit.textChanged.connect(self.__startTimer)
        self.__timer = QtCore.QTimer()
        self.__timer.setInterval(80)
        self.__timer.timeout.connect(self.__filterTable)

        setupIcon(self.addFoodButton, "Add.svg")
        setupIcon(self.importFoodButton, "Import.svg")
        setupIcon(self.editFoodButton, "Edit.svg")
        setupIcon(self.dupFoodButton, "Copy.svg")
        setupIcon(self.exportFoodButton, "Export.svg")
        setupIcon(self.deleteFoodButton, "Delete.svg")

        self.__sourceCheckboxes = dict[FoodSource, QtWidgets.QCheckBox]()
        layout = self.sourcesWidget.layout()
        for source in FoodSource.usable():
            checkbox = QtWidgets.QCheckBox(source.name)
            # FIXME replace this with user preference
            checkbox.setChecked(source in FoodSource.default())
            layout.addWidget(checkbox)
            self.__sourceCheckboxes[source] = checkbox
            checkbox.stateChanged.connect(self.__updateSources)
        layout.addStretch()
        self.__updateSources()

        self.__nutrientValues = {
            "Energy" : self.energyLabel,
            "Protein" : self.proteinLabel,
            "Carbs" : self.carbsLabel,
            "Fiber" : self.fiberLabel,
            "Sugars" : self.sugarLabel,
            "Fat" : self.fatLabel,
            "Water" : self.waterLabel,
            "Saturated" : self.satFatLabel,
            "Cholesterol" : self.cholLabel}
        self.measureSpinBox.valueChanged.connect(self.__updateFoodNutrients)
        self.measureComboBox.currentIndexChanged.connect(self.__updateFoodNutrients)

    def __startTimer(self, _=None):
        """
        Start the timer that will cause the table to filter when it
        times out
        """
        self.__timer.start()

    def __updateSources(self, _=None):
        """
        Update the list of sources that are being shown in the model
        """
        with qtutils.waitCursor():
            sources = {s for (s, c) in self.__sourceCheckboxes.items()
                       if c.isChecked()}
            for s in sources:
                if s not in self.__manager.sources():
                    self.__manager.addSource(s)
            self.__model.setSourcesToUse(sources)

    def __filterTable(self):
        """
        Update the table filter when the user types something
        """
        self.__timer.stop()
        self.__model.setFilterSting(self.searchLineEdit.text())

    def __foodDoubleClicked(self, index: QtCore.QModelIndex):
        """
        Handle a food being double-clicked by showing the food/recipe
        editor.
        """
        food = self.__model.getFood(index.row())

    def __foodSelected(self,
                       selected: QtCore.QItemSelection,
                       _: QtCore.QItemSelection):
        """
        Handle a food being selected by updating the nutrients and servings
        """
        indexes = selected.indexes()
        if not indexes:
            self.foodDetailStack.setCurrentIndex(0)
            self.__currentFood = None
            return
        self.foodDetailStack.setCurrentIndex(1)
        food = self.__model.getFood(indexes[0].row())
        self.__currentFood = food
        measureNames = [m.displayName for m in food.measures]
        with qtutils.blockSignals(self.measureComboBox):
            self.measureComboBox.clear()
            self.measureComboBox.addItems(measureNames)
        with qtutils.blockSignals(self.measureSpinBox):
            self.measureSpinBox.setValue(1)
        self.foodNameLabel.setText(food.name)
        self.__updateFoodNutrients()

    def __updateFoodNutrients(self, _=None):
        """
        Update the nutrient values in the UI based on the selected food
        and the selected serving measure
        """
        if not self.__currentFood:
            return
        nutInfos = self.__manager.nutrientInfos()

        measureSize = self.measureSpinBox.value()
        curIdx = self.measureComboBox.currentIndex()
        measureGrams = self.__currentFood.measures[curIdx].grams
        grams = measureGrams * measureSize
        nutDict = self.__currentFood.nutrientDict(grams)

        for nutName, label in self.__nutrientValues.items():
            ni = nutInfos.getByName(nutName)
            label.setText(formatAmount(nutDict.get(nutName, 0.), ni.unit.value, 15))


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

    def setSourcesToUse(self, sources: set[FoodSource]):
        """
        Set the sources that should be shown in the table.

        Pass an empty set to show all available sources
        """
        self.__sourcesToUse = sources
        self.__updateModelData()

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
            elif col == COL_SOURCE:
                return td.proxy.foodSource.name
            elif col == COL_DATE:
                return td.proxy.publishedDate or date.today()
            return ""

        self.__filteredData.sort(
            key=sortVal, reverse=self.__sortOrder == QtCore.Qt.DescendingOrder)

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
            elif col == COL_SOURCE:
                return td.proxy.foodSource.name
            elif col == COL_DATE:
                return str(td.proxy.publishedDate) if td.proxy.publishedDate else ""
        if role == QtCore.Qt.ToolTipRole:
            if col == COL_DESC:
                return td.proxy.name

    def getFood(self, row: int) -> Food:
        """
        Get the food that is in the given row.
        """
        return self.__manager.getFoodFromProxy(self.__filteredData[row].proxy)
