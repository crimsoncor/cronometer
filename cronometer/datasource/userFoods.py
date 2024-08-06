from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from lxml import etree
from pydantic import BaseModel
from pydantic_xml import BaseXmlModel
from pydantic_xml import attr
from pydantic_xml import element

import cronometer.foods.measure as measure

from cronometer.foods.food import FoodNutrient
from cronometer.foods.food import FoodProxy
from cronometer.foods.food import FoodSource

from .helpers import readIndex

FOOD_INDEX = "foods.index"


def getUserProxies(userDir: Path) -> list[FoodProxy]:
    """
    Load the index of user foods.
    """
    indexFile = userDir / "foods" / FOOD_INDEX
    return readIndex(indexFile, FoodSource.USER)


class EntryType(Enum):
    FOOD = "food"
    RECIPE = "recipe"


class UserFood(BaseXmlModel, tag="food"):
    name: str = attr()
    uid: str = attr()

    foodSource: FoodSource = attr(default=FoodSource.USER)
    entryType: EntryType = attr(default=EntryType.FOOD)

    pCF: float = attr(tag="pcf", default=4.0)
    cCF: float = attr(tag="ccf", default=4.0)
    lCF: float = attr(tag="lcf", default=9.0)

    comments: list[str] = element(tag="comments", default_factory=list)
    measures: list[measure.Measure] = element(tag="measure",
                                              default_factory=list)
    nutrients: list[FoodNutrient] = element(tag="nutrient",
                                            default_factory=list)

    def model_post_init(self, __context):
        if measure.GRAM not in self.measures:
            self.measures.insert(0, measure.GRAM)

    # TODO remove when UserFood is converted to a Food.
    def nutrientDict(self, grams: float):
        """
        Get a dictionary of each nutrient to its value.adjusted for the
        number of grams of the food.

        This is sparse in that it only has nutrients included in the
        food, not the full set of nutrients defined in the nutrientInfos
        """
        mult = grams / 100
        return {n.name : (n.amount * mult) for n in self.nutrients}

    # TODO remove when UserFood is converted to a Food.
    def getMeasureByName(self, name: str) -> measure.Measure:
        """
        Get the food's measure based on the name that is used.
        """
        if not name:
            return measure.GRAM
        return [m for m in self.measures if m.description == name][0]



class RecipeServing(BaseXmlModel, tag="serving"):
    date: datetime = attr(default_factory=datetime.now,
                          exclude=True)
    source: str = attr()
    grams: float = attr()
    food: int = attr()
    meal: int = attr(default=0, exclude=True)
    measure: Optional[str] = attr(default=None)


class UserRecipe(UserFood, tag="recipe"):
    entryType: EntryType = attr(default=EntryType.RECIPE)
    servings: list[RecipeServing] = element(tag="serving",
                                            default_factory=list)


def loadUserFood(userDir: Path, index: int) -> Optional[UserFood]:
    """
    Load the user food with the given id.
    """
    foodFile = userDir / "foods" / f"{index}.xml"
    try:
        with open(foodFile) as f:
            root = etree.parse(f).getroot()
            if root.tag == "food":
                return UserFood.from_xml_tree(root)
            return UserRecipe.from_xml_tree(root)
    except Exception as ex:
        # TODO add logging here
        print(ex)
        return None
