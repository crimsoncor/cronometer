import os
import zipfile

from enum import Enum
from pathlib import Path
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import ConfigDict

from cronometer import DATA_DIR
from cronometer.foods.food import Food
from cronometer.foods.food import FoodProxy
from cronometer.foods.food import FoodSource
from cronometer.util import toolbox

THIS_DIR = Path(os.path.dirname(__file__))

DEPRECATED_ZIP = os.path.join(DATA_DIR, "deprecated.zip")


class FoodType(Enum):
    """
    The type of food from the USDA database.

    The Java version of cronometer only used the LEGACY foods.
    Deprecated foods are legacy foods that are no longer part of the
    data set. The Python cronometer provides a zip file that contains
    these foods so that old files will still load.
    """
    BRANDED = "branded_food"
    EXPERIMENTAL = "experimental_food"
    LEGACY = "sr_legacy_food"
    SAMPLE = "sample_food"
    MARKET_ACQUISITION = "market_acquistion"
    SUB_SAMPLE = "sub_sample_food"
    FOUNDATION = "foundation_food"
    AGRICULTURAL_ACQUISITION = "agricultural_acquisition"
    SURVEY = "survey_fndds_food"
    DEPRECATED = "deprecated"


class UsdaFood(Food):
    """
    A food from the USDA data that includes a foodType field indicating
    the source of the data.
    """
    foodType: FoodType


class UsdaFoodProxy(FoodProxy):
    """
    A food proxy for the USDA foods.
    """
    foodType: FoodType


def _getFoodFromZip(zipPath: Union[str, Path], foodId: str) -> UsdaFood:
    """
    Load a food from a zip file using the given id.

    The id string should contain any sort of padding that is needed
    """
    foodPath = f"{foodId}.json"
    with zipfile.ZipFile(zipPath, "r") as archive:
        with archive.open(foodPath, "r") as f:
            return UsdaFood.model_validate_json(f.read())


def getUsdaProxies(foodType: FoodType) -> list[UsdaFoodProxy]:
    """
    Get the food proxies for one of the USDA food types.
    """
    dataDir = toolbox.getUserDataDir()
    indexFile = os.path.join(dataDir, f"{foodType.value}.index")
    return __readIndex(indexFile, foodType)


def getUsdaFood(proxy: UsdaFoodProxy) -> UsdaFood:
    """
    Get the food identified by the given proxy.
    """
    if proxy.foodType == FoodType.DEPRECATED:
        return getDeprecatedFood(proxy.sourceUID)
    else:
        dataDir = toolbox.getUserDataDir()
        zipFile = os.path.join(dataDir, f"{proxy.foodType.value}.zip")
        return _getFoodFromZip(zipFile, str(proxy.sourceUID))


def getDeprecatedFood(uid: int) -> UsdaFood:
    """
    Get a deprecated food from the data store that ships with
    cronometer.
    """
    foodId = f"{uid:05}"
    return _getFoodFromZip(DEPRECATED_ZIP, foodId)


def getDeprecatedProxies() -> list[UsdaFoodProxy]:
    """
    Get the food proxies for the deprecated USDA legacy foods.

    These foods are shipped with cronometer (since they are no longer
    available in the USDA dataset but may be used in legacy data files.)
    """
    return __readIndex(os.path.join(DATA_DIR, "deprecated.index"),
                       FoodType.DEPRECATED)


def __readIndex(path: Union[str, Path], foodType: FoodType) -> list[UsdaFoodProxy]:
    """
    Read an index file and return the proxies from it.
    """
    toRet = list[UsdaFoodProxy]()
    with open (path, "r") as f:
        for line in f.readlines():
            uid, name = line.split("|", 1)
            proxy = UsdaFoodProxy(name=name,
                                  sourceUID=int(uid),
                                  foodSource=FoodSource.USDA,
                                  foodType=foodType)
            toRet.append(proxy)
    return toRet
