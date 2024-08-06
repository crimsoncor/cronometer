"""
"""
from typing import Any
from typing import Optional

from pydantic import BaseModel
from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets

from cronometer.foods.serving import Serving
from cronometer.user.userDay import UserDay
from cronometer.utils import cleanNumber

COL_FOOD = "Food"
COL_AMOUNT = "Amount"
COL_MEASURE = "Measure"
COL_CALORIES = "Calories"

COLUMNS = [COL_FOOD,
           COL_AMOUNT,
           COL_MEASURE,
           COL_CALORIES]


class _Food(BaseModel):
    servingIndex: int
    """ The index into the servings array in the user day """
    meal: int
    """ The id of the meal this food belongs to """
    row: int
    """ The tree row this food belongs to. """


class _Meal(BaseModel):
    mid: int
    """ The meal number """
    row: int
    """ The tree row this meal belongs to."""


class ServingModel(QtCore.QAbstractItemModel):
    """
    Table model that takes a UserDay and makes it servings
    available to a View.
    """

    """
    To enable editing in your model, you must also implement
    setData(), and reimplement flags() to ensure that
    ItemIsEditable is returned. You can also reimplement
    headerData() and setHeaderData() to control the way the headers
    for your model are presented.
    """
    TESTER = list()
    def __init__(self, parent=None):
        super().__init__(parent)

        self.__userDay: Optional[UserDay] = None

    def setUserDay(self, userDay: Optional[UserDay]):
        self.beginResetModel()
        self.__userDay = userDay
        self.endResetModel()

    def index(self, row: int, column: int, parent: QtCore.QModelIndex) -> QtCore.QModelIndex:
        if not self.hasIndex(row, column, parent) or not self.__userDay:
            return QtCore.QModelIndex()

        if parent.isValid():
            meal = parent.internalPointer().mid
            mealServing = self.__userDay.getMealServings(meal)[row]
            servingIndex = self.__userDay.servings().index(mealServing)
            return self.createIndex(row, column, _Food(servingIndex=servingIndex,
                                                       meal=meal,
                                                       row=row))
        else:
            data = self.__calculateRows()[row]
            return self.createIndex(row, column, data)

    def parent(self, index: QtCore.QModelIndex) -> QtCore.QModelIndex:
        if not index.isValid():
            return QtCore.QModelIndex()

        idxData = index.internalPointer()
        if isinstance(idxData, _Food):
            if idxData.meal != 0:
                for r in self.__calculateRows():
                    if isinstance(r, _Meal) and r.mid == idxData.meal:
                        return self.createIndex(r.row, 0, r)

        return QtCore.QModelIndex()

    def rowCount(self, parent: QtCore.QModelIndex) -> int:
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            return len(self.__calculateRows())
        idxData = parent.internalPointer()
        if isinstance(idxData, _Meal):
            return len(self.__calculateMealRow(idxData.mid))
        return 0

    def columnCount(self, parent: QtCore.QModelIndex) -> int:
        return len(COLUMNS)

    def data(self,
             index: QtCore.QModelIndex,
             role: QtCore.Qt.ItemDataRole=QtCore.Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None

        if self.__userDay is None:
            return None

        if role != QtCore.Qt.DisplayRole:
            return None

        idxData = index.internalPointer()
        col = COLUMNS[index.column()]
        if isinstance(idxData, _Meal):
            if col == COL_FOOD:
                return f"Meal {idxData.mid}"
            elif col == COL_CALORIES:
                # FIXME hard-coded calories index here. do better,
                return cleanNumber(self.__userDay.getMealNutrition(idxData.mid)[0])
            elif col == COL_AMOUNT:
                return None
            elif col == COL_MEASURE:
                return None
        elif isinstance(idxData, _Food):
            if col == COL_FOOD:
                return self.__userDay.getFood(idxData.servingIndex).name
            elif col == COL_CALORIES:
                # FIXME hard-coded calories index here. do better.
                return cleanNumber(self.__userDay.getNutrition(idxData.servingIndex)[0])
            elif col == COL_AMOUNT:
                return cleanNumber(self.__userDay.getAmount(idxData.servingIndex),
                                   decimal=2)
            elif col == COL_MEASURE:
                return self.__userDay.servings()[idxData.servingIndex].measure or "g"
        return None

    def __calculateRows(self) -> list[_Meal | _Food]:
        rows = list()
        meals = set[int]()
        row = 0
        if self.__userDay:
            for i, e in enumerate(self.__userDay.servings()):
                if e.meal == 0:
                    rows.append(_Food(servingIndex=i,
                                      meal=0,
                                      row=row))
                    row += 1
                elif e.meal not in meals:
                    rows.append(_Meal(mid=e.meal,
                                      row=row))
                    meals.add(e.meal)
                    row += 1
        self.TESTER.extend(rows)
        return rows

    def __calculateMealRow(self, meal: int) -> list[_Food]:
        """
        """
        rows = list()
        if self.__userDay:
            row = 0
            for i, e in enumerate(self.__userDay.servings()):
                if e.meal == meal:
                    rows.append(_Food(servingIndex=i,
                                      meal=meal,
                                      row=row))
                    row +=1
        self.TESTER.extend(rows)
        return rows

    def __getServing(self, meal: int, index: int) -> Serving:
        if meal == 0:
            return self.__userDay.servings()[index]
        return self.__userDay.getMealServings(meal)[index]
