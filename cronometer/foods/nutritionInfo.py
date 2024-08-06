"""
Information about the different nutrients that make up food and their
recommended daily intakes.
"""
import os

from enum import Enum
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import computed_field
from pydantic_xml import BaseXmlModel
from pydantic_xml import attr
from pydantic_xml import element

from cronometer import DATA_DIR
from cronometer.targets.dri import DRI
from cronometer.utils import static_vars


class NutrientCategory(Enum):
    """
    The gropuing family for the nutrient.
    """
    LIPIDS = "Lipids"
    MINERALS = "Minerals"
    MACRO = "General"
    ANIMO_ACIDS = "Amino Acids"
    VITAMINS = "Vitamins"


class NutrientUnit(Enum):
    """
    The unit of measure that a nutrient uses.
    """
    GRAM = "g"
    CALORIE = "kcal"
    MILLIGRAM = "mg"
    MICROGRAM = "µg"
    IU = "iu"
    PH = "ph"
    SPECIFIC_GRAVITY = "sp_gr"
    KILOJOULE = "kj"
    MICROGRAM_RE = "mcg_re"
    MILLIGRAM_ATR = "mg_ate"
    UMOL_TE = "umol_te"
    MILLIGRAM_GAE = "mg_gae"


class NutrientInfo(BaseModel):
    """
    The NutrientInfo used in the python cronometer.
    """
    model_config = ConfigDict(frozen=True)

    name: str
    unit: NutrientUnit
    category: NutrientCategory
    rdi: float
    parentName: Optional[str]
    legacyIds: list[float]
    """ The legacy usda ids that identify this nutrient"""
    usdaIds: list[int]
    """ The new usda ids from the CSV data that identify the nutrient"""
    sparse: bool
    track: bool
    dris: list[DRI]
    cronIndex: int
    """ The index for the nutrient in cronometer data"""


class NutrientInfos(BaseModel, frozen=True):
    nutrients: list[NutrientInfo]

    def __init__(self, **data):
        super().__init__(**data)
        object.__setattr__(self,
                           "__nutrients",
                           sorted(self.nutrients, key=lambda x: x.cronIndex))
        object.__setattr__(self,
                           "__nutIndexDict",
                           {n.name : n.cronIndex for n in self.nutrients})

    def getByName(self, name: str) -> Optional[NutrientInfo]:
        """
        Get the nutrient info by name
        """
        try:
            return next(n for n in self.nutrients if n.name == name)
        except StopIteration:
            return None

    def indexOfName(self, name: str) -> int:
        """
        Get the index for the given nutrient name
        """
        return self.__nutIndexDict.get(name)

    def ordering(self) -> list[str]:
        """
        Get the list of nutrients in order
        """
        return [n.name for n in self.nutrients]

    def nutrientDictToTuple(self, nutrientDict: dict[str, float]) -> tuple:
        """
        Generate a tuple of nutrient values in the smae order as the list
        of nutrients in this class.

        nutrientDict should have a key that is the nutrient name and the
        value of the amount of the nutrient. Zero will be inserted into the
        tuple for any value that is not in the dict.
        """
        return tuple((nutrientDict.get(n.name, 0) for n in self.nutrients))


def loadNutrientInfo() -> NutrientInfos:
    """
    Load the nutrient info file from the cronometer data directory
    """
    with open(os.path.join(DATA_DIR, "nutrients.json"), "r") as f:
        return NutrientInfos.model_validate_json(f.read())


class UsdaIdx(BaseXmlModel):
    """
    Here because pydantic-xml does not appear to like computed fields which
    are lists of primitives. So we have to wrap the float in an XML model so that
    we can have the computed field. Thankfully this is only used during the
    conversion process and not as part of the python app.
    """
    index: float = attr()


@static_vars(nid=0)
def _getNextId() -> int:
    """
    Get the next nutrient info id
    """
    toRet = _getNextId.nid
    _getNextId.nid += 1
    return toRet


class LegacyNutrientInfo(BaseXmlModel, tag="nutrient"):
    """
    The nutrient info data loaded from the cronometer java xml file.

    This is used in the usdaFoodLoader code to generate the new
    nutritionInfo json file. This should not be used in new code.
    """
    name: str = attr(tag="name")
    unit: NutrientUnit = attr()
    category: NutrientCategory = attr()
    rdi: float = attr(tag="dv", default=0.0)
    parentName: Optional[str] = attr(tag="parent", default=None)
    usdaStr: str = attr(name='usda', default="", exclude=True)
    sparse: bool = attr(default=False)
    track: bool = attr(default=True)
    dris: list[DRI] = element(tag="rda", default_factory=list)
    index: int = attr(default_factory=_getNextId)

    @computed_field
    def usda(self) -> list[UsdaIdx]:
        s = self.usdaStr.strip()
        return [] if not s else [UsdaIdx(index=float(s)) for s in s.split(",")]


class LegacyNutrientInfos(BaseXmlModel, tag="nutrients"):
    """
    Serialization wrapper for LegacyNutritionInfo

    This is used in the usdaFoodLoader code to generate the new
    nutritionInfo json file. This should not be used in new code.
    """
    nutrients: list[LegacyNutrientInfo] = element()
