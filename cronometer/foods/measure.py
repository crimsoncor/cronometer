"""
"""

from pydantic_xml import attr
from pydantic_xml import BaseXmlModel


class Measure(BaseXmlModel, tag="measure"):
    grams: float = attr()
    amount: float = attr()
    description: str = attr(name="name")


GRAM = Measure(grams=1.0, amount=1.0, description="g")
