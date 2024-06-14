"""
"""

from enum import Enum
from typing import Any
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import computed_field
from pydantic import field_validator
from pydantic import Field
from pydantic import ValidationInfo
from pydantic_xml import attr
from pydantic_xml import BaseXmlModel
from pydantic_xml import element

from cronometer.targets.dri import DRI
from cronometer.utils import static_vars


@static_vars(nid=0)
def _getNextId() -> int:
    """
    Get the next nutrient info id
    """
    toRet = _getNextId.nid
    _getNextId.nid += 1
    return toRet


class NutrientCategory(Enum):
    LIPIDS = "Lipids"
    MINERALS = "Minerals"
    MACRO = "General"
    ANIMO_ACIDS = "Amino Acids"
    VITAMINS = "Vitamins"


class UsdaIdx(BaseXmlModel):
    """
    Here because pydantic-xml does not appear to like computed fields which
    are lists of primitives. So we have to wrap the int in an XML model so that
    we can have the computed field. Would really like to change this.
    """
    index: int = attr()

class NutrientInfo(BaseXmlModel, tag="nutrient"):
    name: str = attr(tag="name")
    unit: str = attr()
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
        return [] if not s else [UsdaIdx(index=int(s)) for s in s.split(",")]


class NutrientInfos(BaseXmlModel, tag="nutrients"):
    nutrients: list[NutrientInfo] = element()

    def nutrientsInCategory(self, nc: NutrientCategory):
        return [n for n in self.nutrients if n.category == nc]
