"""
"""

from pydantic_xml import BaseXmlModel
from pydantic_xml import attr


class Measure(BaseXmlModel, tag="measure"):
    grams: float = attr()
    amount: float = attr()
    description: str = attr(name="name")

    @property
    def displayName(self) -> str:
        """
        The display name for the measure.

        This combines amount (if it is non-zero) with description
        """
        if self.amount == 0.0:
            return self.description
        return f"{self.amount:.4} {self.description}"



GRAM = Measure(grams=1.0, amount=1.0, description="g")
