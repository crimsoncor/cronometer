"""

"""

from pydantic import BaseModel
from .measure import Measure
from typing import Tuple


class Food(BaseModel):
    name: str
    measures: list[Measure]
    nutrients: Tuple[int]

    comment: str
    pCF: float = 4.0
    fCF: float = 9.0
    cCF: float = 4.0

    dataSource: object
    sourceUID: str

    # def nutrientAmount()
