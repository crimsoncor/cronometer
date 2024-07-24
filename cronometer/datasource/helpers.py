
import re

from pathlib import Path
from typing import Union

from cronometer.foods.food import FoodProxy
from cronometer.foods.food import FoodSource

INDEX_PAT = re.compile(r"(?:(\d+)\|\|\|)?(\d+)\|(.*)")


def readIndex(path: Union[str, Path],
              foodSource: FoodSource) -> list[FoodProxy]:
    """
    Read an index file and return the proxies from it.
    """
    toRet = list[FoodProxy]()
    with open (path, "r") as f:
        for line in f.readlines():
            res = INDEX_PAT.match(line)
            legacyId = int(res.group(1)) if res.group(1) else None
            uid = int(res.group(2))
            name = res.group(3)
            proxy = FoodProxy(name=name,
                              sourceUID=int(uid),
                              foodSource=foodSource,
                              legacyUID=legacyId)
            toRet.append(proxy)
    return toRet
