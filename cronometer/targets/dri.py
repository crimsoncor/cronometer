"""
"""

from enum import Enum
from pydantic_xml import BaseXmlModel
from pydantic_xml import attr
from typing import Optional


class DRI_Gender(Enum):
    ALL = "all"
    MALE = "male"
    FEMALE = "female"


class DRI(BaseXmlModel, tag="rda"):
    min_age: float = attr()
    max_age: float = attr(default=10000)
    gender: DRI_Gender = attr(default=DRI_Gender.ALL)
    status: Optional[str] = attr(default=None)
    RDA: float = attr(name="amount", default=-1)
    TUL: float = attr(name="tul", default=-1)
