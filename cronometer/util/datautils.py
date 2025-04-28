"""
Utilities for working with data and formatting
"""

def asPercentage(value: float) -> str:
    """
    Format a float as a percentage string
    """
    return f"{value:.1%}"


def formatAmount(value: float, suffix: str, maxPlaces: int=15) -> str:
    """
    Format the given value and combine with the suffix to get string
    that is no more than maxPlaces.

    Suffix is assumed to be space separated
    """
    strVal = f"{value:.2f}".rstrip('0').rstrip('.') + f" {suffix}"
    if len(strVal) <= maxPlaces:
        return strVal
    sciPlaces = maxPlaces - 6 - len(suffix) - 1 # 4 spaces for e+08
    strVal = f"{value:.{sciPlaces}e} {suffix}"
    if len(strVal) <= maxPlaces:
        return strVal
    return strVal[:maxPlaces -1]
