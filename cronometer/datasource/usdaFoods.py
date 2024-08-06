import os
import zipfile

from pathlib import Path
from typing import Union

from cronometer import DATA_DIR
from cronometer.foods.food import Food
from cronometer.foods.food import FoodProxy
from cronometer.foods.food import FoodSource
from cronometer.util import toolbox

from .helpers import readIndex

DEPRECATED_ZIP = os.path.join(DATA_DIR, "deprecated.zip")


def _getFoodFromZip(zipPath: Union[str, Path], foodId: str) -> Food:
    """
    Load a food from a zip file using the given id.

    The id string should contain any sort of padding that is needed
    """
    foodPath = f"{foodId}.json"
    with zipfile.ZipFile(zipPath, "r") as archive:
        with archive.open(foodPath, "r") as f:
            return Food.model_validate_json(f.read())


def getUsdaProxies(foodType: FoodSource) -> list[FoodProxy]:
    """
    Get the food proxies for one of the USDA food types.
    """
    dataDir = toolbox.getUserDataDir()
    indexFile = os.path.join(dataDir, f"{foodType.value}.index")
    return readIndex(indexFile, foodType)


def getLegacyIdMapping() -> dict[int, int]:
    """
    Get the mapping from legacy Id to new Id for all the foods in the
    LEGACY FoodSource.

    This is needed to convert legacy data to work in the new python
    cronometer.

    The key is the legacy id and the value is the new USDA id.
    """
    proxies = getUsdaProxies(FoodSource.LEGACY)
    return {p.legacyUID : p.sourceUID for p in proxies if p.legacyUID}


def loadUsdaFood(source: FoodSource, index: int) -> Food:
    """
    Get the food identified by the given proxy.
    """
    if source == FoodSource.DEPRECATED:
        return loadDeprecatedFood(index)
    else:
        dataDir = toolbox.getUserDataDir()
        zipFile = os.path.join(dataDir, f"{source.value}.zip")
        return _getFoodFromZip(zipFile, str(index))


def loadDeprecatedFood(uid: int) -> Food:
    """
    Get a deprecated food from the data store that ships with
    cronometer.
    """
    foodId = f"{uid:05}"
    return _getFoodFromZip(DEPRECATED_ZIP, foodId)


def getDeprecatedProxies() -> list[FoodProxy]:
    """
    Get the food proxies for the deprecated USDA legacy foods.

    These foods are shipped with cronometer (since they are no longer
    available in the USDA dataset but may be used in legacy data files.)
    """
    return readIndex(os.path.join(DATA_DIR, "deprecated.index"),
                     FoodSource.DEPRECATED)
