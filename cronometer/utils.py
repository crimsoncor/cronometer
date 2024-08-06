from typing import Union


def static_vars(**kwargs):
    def decorate(func):
        for k, v in kwargs.items():
            setattr(func, k, v)
        return func
    return decorate


def cleanNumber(number: Union[int, float], decimal:int=1):
    """
    Cleanly format a number.

    If this is an int value, there will be no decimal.
    """
    if isinstance(number, int) or number.is_integer():
        return str(int(number))
    fstr = f"{{number:.{decimal}f}}"
    return fstr.format(number=number).rstrip("0")
