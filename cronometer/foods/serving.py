import os
import time

from datetime import date as dtdate
from datetime import datetime

from pydantic import BaseModel
from pydantic import computed_field
from pydantic_xml import BaseXmlModel
from pydantic_xml import attr

from cronometer.foods.food import FoodSource
from cronometer.util import toolbox


class Serving(BaseModel):
    """
    A user food serving.
    """
    date: dtdate
    source: FoodSource
    food: int
    grams: float
    measure: str = ""
    meal: int = 0


class LegacyServing(BaseXmlModel, tag="serving"):
    """
    A user food serving from the legacy java cronometer.
    """
    dtime: datetime = attr("date", alias="date", exclude=True)
    meal: int = attr("meal", default=0)
    measure: str = attr("measure", default="")
    source: str = attr("source")
    grams: float = attr("grams")
    food: int = attr("food")

    @computed_field
    def date(self) -> dtdate:
        return self.dtime.date()


class _LegacyServings(BaseXmlModel, tag="servings"):
    """
    XML Parsing wrapper for legacy XML data.
    """
    servings: list[LegacyServing]


def loadLegacyServings(userName: str) -> list[LegacyServing]:
    """
    Get the list of servings for the given user
    """
    profileDir = toolbox.getUserProfileDir(userName)
    servingsFile = os.path.join(profileDir, "servings.xml")

    with open(servingsFile, 'r') as f:
        return _LegacyServings.from_xml(f.read()).servings


def convertServings(legacy: list[LegacyServing],
                    legacyMap: dict[int, int],
                    deprecatedIds: list[int]) -> list[Serving]:
    """
    Convert the legacy serving data into new servings, including
    converting all the old food id values into new ones.
    """
    toRet = list[Serving]()
    for ls in legacy:
        if ls.source == "USDA":
            if ls.food in deprecatedIds:
                source = FoodSource.DEPRECATED
            else:
                source = FoodSource.LEGACY
        elif ls.source == "CRDB":
            source = FoodSource.CRDB
        elif ls.source == "My Foods":
            source = FoodSource.USER
        else:
            raise ValueError(
                f"Cannot convert legacy source {ls.source} to a FoodSource")
        uid = legacyMap[ls.food] if source == FoodSource.LEGACY else ls.food
        serving = Serving(date=ls.date,
                          source=source,
                          food=uid,
                          grams=ls.grams,
                          measure=ls.measure,
                          meal=ls.meal)
        toRet.append(serving)
    return toRet
