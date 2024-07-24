"""

"""
from enum import Enum
from typing import Any
from typing import Optional

from pydantic import BaseModel
from pydantic import field_validator
from pydantic_xml import BaseXmlModel
from pydantic_xml import attr

from .measure import Measure


class FoodSource(Enum):
    """
    Where the data for this food was loaded from.

    The Java version of cronometer only used the LEGACY foods and CRDB
    foods. The CRDB database is not available online so it has been
    packaged and included with the python cronometer.

    DEPRECATED foods are LEGACY  foods that are no longer part of the
    data set. The Python cronometer provides a zip file that contains
    these foods so that old files will still load.
    """
    # User created foods
    USER = "user"

    # Data from the USA
    BRANDED = "branded_food"
    EXPERIMENTAL = "experimental_food"
    LEGACY = "sr_legacy_food"
    SAMPLE = "sample_food"
    MARKET_ACQUISITION = "market_acquistion"
    SUB_SAMPLE = "sub_sample_food"
    FOUNDATION = "foundation_food"
    AGRICULTURAL_ACQUISITION = "agricultural_acquisition"
    SURVEY = "survey_fndds_food"

    # Datasets not longer available that are packaged with cronometer.
    DEPRECATED = "deprecated"
    CRDB = "crdb"


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
    legacyUID: Optional[int] = None


class Food(BaseModel):
    name: str
    uid: int
    """ The id for the food."""
    legacyUID: Optional[int] = None
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

    @field_validator('cCF', mode="before")
    @classmethod
    def _ensure_carb(cls, v: Any):
        """
        Pydantic validator that lets us pass None for conversion factor
        """
        if v is None:
            return 4.0
        return v

    @field_validator('pCF', mode="before")
    @classmethod
    def _ensure_protein(cls, v: Any):
        """
        Pydantic validator that lets us pass None for conversion factor
        """
        if v is None:
            return 4.0
        return v

    @field_validator('lCF', mode="before")
    @classmethod
    def _ensure_lipid(cls, v: Any):
        """
        Pydantic validator that lets us pass None for conversion factor
        """
        if v is None:
            return 9.0
        return v
