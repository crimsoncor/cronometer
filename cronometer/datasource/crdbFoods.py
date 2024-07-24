"""
Foods that came from the crdb_005.jar file in the latest java version
of cronometer. Included here for completeness in case existing data
files were using these foods.

This lovely data source also includes recipes, so it has some extra
spicy handling necessary.
"""
import os
import zipfile

from typing import Union

from pydantic_core import from_json

from cronometer import DATA_DIR
from cronometer.datasource.userFoods import UserFood
from cronometer.datasource.userFoods import UserRecipe
from cronometer.foods.food import FoodProxy
from cronometer.foods.food import FoodSource

from .helpers import readIndex

CRDB_ZIP = os.path.join(DATA_DIR, "crdb_005.zip")


def _getFoodFromZip(foodId: str) -> Union[UserFood, UserRecipe]:
    """
    Load a food or recipe from the crdb zip file using the given id.

    The id string should contain any sort of padding that is needed
    """
    foodPath = f"{foodId}.json"
    with zipfile.ZipFile(CRDB_ZIP, "r") as archive:
        with archive.open(foodPath, "r") as f:
            data = from_json(f.read())
            if data.get("entryType") == "recipe":
                return UserRecipe.model_validate(data)
            else:
                return UserFood.model_validate(data)


def getCRDBProxies() -> list[FoodProxy]:
    """
    Get the food proxies for the CRDB legacy foods.

    These foods are shipped with cronometer (since they are no longer
    available in the USDA dataset but may be used in legacy data files.)
    """
    return readIndex(os.path.join(DATA_DIR, "crdb_005.index"), FoodSource.CRDB)


def getCRDBFood(proxy: FoodProxy) -> Union[UserFood, UserRecipe]:
    """
    Get the food or receipt identified by the given proxy
    """
    return _getFoodFromZip(f"{proxy.sourceUID:05}")
