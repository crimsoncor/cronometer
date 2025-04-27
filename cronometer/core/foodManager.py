"""
"""
from typing import Optional

from Qt import QtCore

from cronometer.core.errors import MessageError
from cronometer.datasource import crdbFoods
from cronometer.datasource import usdaFoods
from cronometer.datasource import userFoods
from cronometer.foods.food import Food
from cronometer.foods.food import FoodProxy
from cronometer.foods.food import FoodSource
from cronometer.foods.nutritionInfo import NutrientInfos
from cronometer.util import toolbox


# TODO Add a special wrapper for recently used branded foods.
class _FoodSourceWrapper(object):
    """
    A wrapper for a food source that handles loading the foods and
    providing access to them.

    Designed to be used inside the FoodManager.

    The index referred to here is always the index into the list of foods
    from the manager. It is not the uid of the food in question.
    """
    def __init__(self, source: FoodSource):
        """
        Create a new wrapper
        """
        self.__source = source
        if source == FoodSource.USER:
            self.__proxies = userFoods.getUserProxies(toolbox.getUserAppDirectory())
        elif source == FoodSource.CRDB:
            self.__proxies = crdbFoods.getCRDBProxies()
        elif source == FoodSource.DEPRECATED:
            self.__proxies = usdaFoods.getDeprecatedProxies()
        else:
            self.__proxies = usdaFoods.getUsdaProxies(source)

        # This is a mapping of the food UID to the index in the source
        self.__uidToIndex = dict[int, int]()
        for index, proxy in enumerate(self.__proxies):
            self.__uidToIndex[proxy.sourceUID] = index

        self.__foods = dict[int, Food]()

    def getFood(self, index: int) -> Food:
        """
        Get the food with the given index.
        """
        if index in self.__foods:
            return self.__foods[index]

        if self.__source == FoodSource.USER:
            # TODO need to update UserFood to be a Food type.
            food = userFoods.loadUserFood(toolbox.getUserAppDirectory(), index)
        elif self.__source == FoodSource.CRDB:
            food = crdbFoods.loadCRDBFood(index)
        else:
            food = usdaFoods.loadUsdaFood(self.__source, index)

        self.__foods[index] = food
        return food

    def getFoodIndex(self, uid: int) -> int:
        """
        Given a source uid for a food, return the index that maps to that
        food in this wrapper.
        """
        return self.__uidToIndex[uid]

    def getFoodCount(self) -> int:
        """
        Get the toal number of foods in the dictionary.
        """
        return len(self.__proxies)

    def getFoodProxy(self, index: int) -> FoodProxy:
        """
        Get the proxy for the given index
        """
        return self.__proxies[index]

    def getFoodProxies(self) -> list[FoodProxy]:
        """
        Get all the food proxies
        """
        return list(self.__proxies)

    def getFoodName(self, index: int) -> str:
        """
        Get the name of the food with the given index.
        """
        return self.__proxies[index].name

    def getFoodNames(self) -> list[str]:
        """
        Get a list of all the food names in index order.
        """
        return [p.name for p in self.__proxies]


class FoodManager(QtCore.QObject):
    """
    Class that contains pointers to all the food sources that have
    been loaded and provides easy access to them.
    """
    sourceAdded = QtCore.Signal()
    sourceRemoved = QtCore.Signal()

    def __init__(self, nutrientInfos: NutrientInfos):
        """
        Create a new food manager
        """
        super().__init__(None)
        self.__foodSources = dict[FoodSource, _FoodSourceWrapper]()
        self.__nutrientInfo = nutrientInfos

    def __getSource(self, source: FoodSource) -> _FoodSourceWrapper:
        if source not in self.__foodSources:
            raise MessageError(f"Food Source {source.value} is not loaded. Please"
                               f" enable it in preferences to use. ")
        return self.__foodSources[source]

    def sources(self) -> list[FoodSource]:
        """
        Get the list of sources this that were loaded.
        """
        return list(self.__foodSources)

    def addSource(self, source: FoodSource):
        """
        Add a new food souce to the manager
        """
        if source not in self.__foodSources:
            self.__foodSources[source] = _FoodSourceWrapper(source)
            self.sourceAdded.emit()

    def removeSource(self, source: FoodSource):
        """
        Remove a loaded food source
        """
        # Only emit if the source was in the dict
        if self.__foodSources.pop(source, None):
            self.sourceRemoved.emit()

    def getFoodProxy(self, source: FoodSource, index: int) -> FoodProxy:
        """
        Get a proxy by index
        """
        return self.__getSource(source).getFoodProxy(index)

    def getFoodProxies(self, source: FoodSource) -> list[FoodProxy]:
        """
        Get all the proxies for the source
        """
        return self.__getSource(source).getFoodProxies()

    def getFood(self, source: FoodSource, index: int) -> Food:
        """
        Get a food by index
        """
        return self.__getSource(source).getFood(index)

    def getFoodFromProxy(self, proxy: FoodProxy) -> Food:
        """
        Get a food from its proxy
        """
        return self.getFood(proxy.foodSource, proxy.sourceUID)

    def getFoodCount(self, source: Optional[FoodSource]=None) -> int:
        """
        Get the total number of foods from a source or from all sources.

        Pass None for source to get total count of all loaded sources.
        """
        if source is None:
            return sum((fs.getFoodCount() for fs in (self.__foodSources.values())))
        return self.__getSource(source).getFoodCount()

    def getFoodNames(self, source: FoodSource) -> list[str]:
        """
        Get the names of all the foods in the source
        """
        return self.__getSource(source).getFoodNames()

    def getFoodIndex(self, source: FoodSource, uid: int) -> int:
        """
        Given a source and a  uid for a food, return the index that maps to
        that food.
        """
        return self.__getSource(source).getFoodIndex(uid)

    def nutrientInfo(self) -> NutrientInfos:
        """
        Get the Nutrient Info.
        """
        return self.__nutrientInfo
