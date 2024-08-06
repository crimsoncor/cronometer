"""
A wrapper for a single day for a single user.
"""

from collections import defaultdict

from cronometer.core.foodManager import FoodManager
from cronometer.foods.food import Food
from cronometer.foods.food import FoodNutrient
from cronometer.foods.serving import Serving


class UserDay(object):

    def __init__(self, manager: FoodManager, servings: list[Serving]):
        """
        Create a new UserDay
        """
        self.__manager = manager
        self.__servings = servings

        self.__foods = list()
        self.__servingSize = list()
        self.__meals = list[int]()
        self.__servingsByMeal = dict[int, list[Serving]]

        self.__nutrition = tuple()
        self.__mealNutrition = dict[int, tuple]()
        self.__servingTuples = list[tuple]()

        self.__build()

    def servings(self) -> list[Serving]:
        return self.__servings

    def getFood(self, index: int) -> Food:
        """
        Get the Food by serving index
        """
        return self.__foods[index]

    def getNutrition(self, index: int) -> tuple:
        """
        Get the nutrition tuple by serving index
        """
        return self.__servingTuples[index]

    def getAmount(self, index: int) -> float:
        """
        Get the amount of the food by serving index
        """
        return self.__servingSize[index]

    def getMeals(self) -> list[int]:
        """
        Get the list of meal indexes that the user has associated
        servings with.
        """
        return self.__meals

    def getMealServings(self, meal: int) -> list[Serving]:
        return [s for s in self.__servings if s.meal == meal]

    def getMealNutrition(self, meal: int) -> tuple:
        return self.__mealNutrition[meal]

    def __build(self):
        """
        Construct all the data structures that will make querying the
        day's data easy.
        """
        self.__foods = list()
        self.__servingSize = list()
        meals = set[int]()
        self.__servingsByMeal = defaultdict[int, list[Serving]](list)

        nutInfo = self.__manager.nutrientInfo()

        mealTuples = defaultdict[int, list](list)
        self.__servingTuples = list[tuple]()

        for s in self.__servings:
            food = self.__manager.getFood(s.source, s.food)
            self.__foods.append(food)

            nutrientDict = food.nutrientDict(s.grams)
            nutrientTuple = nutInfo.nutrientDictToTuple(nutrientDict)
            self.__servingTuples.append(nutrientTuple)

            measure = food.getMeasureByName(s.measure)
            servingSize = s.grams / measure.grams
            self.__servingSize.append(servingSize)

            if s.meal != 0:
                meals.add(s.meal)
                mealTuples[s.meal].append(nutrientTuple)
                self.__servingsByMeal[s.meal].append(s)

        self.__nutrition = tuple((sum(a) for a in zip(*self.__servingTuples)))
        self.__mealNutrition.clear()
        for meal, tup in mealTuples.items():
            self.__mealNutrition[meal] = tuple((sum(a) for a in zip(*tup)))

        self.__meals = sorted(meals)
