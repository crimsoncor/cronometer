"""
"""

from cronometer.core.errors import MessageError
from cronometer.datasource import crdbFoods
from cronometer.datasource import usdaFoods
from cronometer.datasource import userFoods
from cronometer.foods.food import Food
from cronometer.foods.food import FoodProxy
from cronometer.foods.food import FoodSource
from cronometer.foods.nutritionInfo import NutrientInfos
from cronometer.util import toolbox


class _FoodSourceWrapper(object):
    """
    A wrapper for a food source that handles loading the foods and
    providing access to them.

    Designed to be used inside the FoodManager.
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



class FoodManager(object):
    """
    Class that contains pointers to all the food sources that have
    been loaded and provides easy access to them.
    """
    def __init__(self, nutrientInfos: NutrientInfos):
        """
        """
        self.__foodSources = dict[FoodSource, _FoodSourceWrapper]()
        self.__nutrientInfo = nutrientInfos

    def __getSource(self, source: FoodSource) -> _FoodSourceWrapper:
        if source not in self.__foodSources:
            raise MessageError(f"Food Source {source.value} is not loaded. Please"
                               f" enable it in preferences to use. ")
        return self.__foodSources[source]

    def addSource(self, source: FoodSource):
        """
        Add a new food souce to the manager
        """
        self.__foodSources[source] = _FoodSourceWrapper(source)

    def removeSource(self, source: FoodSource):
        """
        Remove a loaded food source
        """
        self.__foodSources.pop(source, None)

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

    def nutrientInfo(self) -> NutrientInfos:
        """
        Get the Nutrient Info.
        """
        return self.__nutrientInfo
