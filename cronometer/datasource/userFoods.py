
from datetime import datetime
from lxml import etree
from pathlib import Path
from pydantic import BaseModel
from pydantic_xml import attr
from pydantic_xml import BaseXmlModel
from pydantic_xml import element
from typing import Optional

from cronometer.foods.food import FoodNutrient
import cronometer.foods.measure as measure


FOOD_INDEX = "foods.index"


class FoodIndexEntry(BaseModel):
    index: int
    name: str


def loadIndex(userDir: Path) -> list[FoodIndexEntry]:
    """
    Load the index of user foods.
    """
    toRet = list()
    indexFile = userDir / "foods" / FOOD_INDEX
    try:
        with open(indexFile) as f:
            for line in f.readlines():
                split = line.split("|")
                if len(split) == 2:
                    toRet.append(FoodIndexEntry(index=int(split[0]),
                                                name=split[1].strip()))
        toRet.sort(key=lambda x: x.index)
    except FileNotFoundError:
        pass
    return toRet


class UserFood(BaseXmlModel, tag="food"):
    name: str = attr()
    uid: str = attr()

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


class RecipeServing(BaseXmlModel, tag="serving"):
    date: datetime = attr()
    source: str = attr()
    grams: float = attr()
    food: int = attr()


class UserRecipe(UserFood, tag="recipe"):
    servings: list[RecipeServing] = element(tag="serving",
                                            default_factory=list)


def loadFood(userDir: Path, index: int) -> Optional[UserFood]:
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
