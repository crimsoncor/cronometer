import os
import platform

from enum import Enum
from pathlib import Path

APP_NAME = "cronometer"


class OperatingSystem(Enum):
    WINDOWS = "windows"
    MAC = "mac"
    LINUX = "linux"


def operatingSystem() -> OperatingSystem:
    """
    Get the operating system that is being run on.
    """
    system = platform.system()
    if system.startswith('Windows'):
        return OperatingSystem.WINDOWS
    elif system.startswith('Darwin'):
        return OperatingSystem.MAC
    return OperatingSystem.LINUX


def getUserDirectory() -> Path:
    """
    Get the system specific user data directory.

    Returns the appropriate location to store application
    data for the user, on the current platform.
    """
    home = Path.home()
    opSys = operatingSystem()
    if opSys == OperatingSystem.MAC:
        return home / "Library" / "Preference"
    elif opSys == OperatingSystem.WINDOWS:
        return home / "Application Data"
    return home


def getUserAppDirectory(appName: str=APP_NAME) -> Path:
    """
    Get the cronometer directory.
    """
    if operatingSystem() in (OperatingSystem.WINDOWS, OperatingSystem.MAC):
        return getUserDirectory() / appName
    return getUserDirectory() / f".{appName}"


def getUserDataDir() -> Path:
    """
    Get the cronometer sub-directory where generated usda data is stored.
    """
    return getUserAppDirectory() / "data"
