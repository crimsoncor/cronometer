"""

"""
from enum import Enum
from typing import Optional

from pydantic import BaseModel
from pydantic_xml import BaseXmlModel
from pydantic_xml import attr

from .measure import Measure


class FoodSource(Enum):
    """
    Where this food was loaded from
    """
    USDA = "usda"
    USER = "user"


class FoodNutrient(BaseXmlModel, tag="nutrient"):
    """
    A single nutrient entry in a food.

    This uses the XML base model so that the UserFood class can
    make use of it as well.
    """
    name: str = attr()
    amount: float = attr()


class FoodProxy(BaseModel):
    """
    A lightweight proxy for a food that will be used to load the actual
    food when the data is needed.
    """
    name: str
    sourceUID: int
    foodSource: FoodSource


class Food(BaseModel):
    name: str
    sourceUID: int
    legacyUID: Optional[int]
    """ The legacy food id value from the old USDA data used in the java cronometer.
        Empty for user foods and new USDA data. """
    pCF: float = 4.0
    cCF: float = 4.0
    lCF: float = 9.0
    comments: list[str]
    measures: list[Measure]
    nutrients: list[FoodNutrient]

    foodSource: FoodSource

    def nutrientValueByName(self, name: str) -> float:
        """
        Get a nutrient value by name.

        Will return zero if a nutrient is not set.
        """
        for nut in self.nutrients:
            if nut.name == name:
                return nut.amount
        return 0.0

    def setNutrientByName(self, name: str, amount: float):
        """
        Set a nutrient by name
        """
        for nut in self.nutrients:
            if nut.name == name:
                nut.amount = amount
                return
        fn = FoodNutrient(name=name, amount=amount)
        self.nutrients.append(fn)
