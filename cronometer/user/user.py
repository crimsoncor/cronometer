import os

from datetime import date
from typing import Optional

from pydantic import BaseModel
from pydantic_xml import BaseXmlModel
from pydantic_xml import attr
from pydantic_xml import element

import cronometer.util.toolbox as toolbox

BD_DAY = "birthdate.day"
BD_MONTH = "birthdate.month"
BD_YEAR = "birthdate.year"


class LegacyGeneralSetting(BaseXmlModel, tag="General"):
    """
    A single general settings entry in the Java cronometer.
    """
    name: str = attr()
    value: str = attr()


class LegacyUserSetting(LegacyGeneralSetting, tag="User"):
    """
    A single user settings entry in the Java cronometer
    """
    username: str = attr()


class User(BaseModel):
    """
    A user in the cronometer system.
    """
    username: str
    settings: list[LegacyGeneralSetting]

    # Pydantic private members.
    _birthDate: date
    _settingsDict: dict[str, str]

    def __init__(self, **data):
        """
        Overwrite the pydantic init to initialize the private members.
        """
        super().__init__(**data)
        self._settingsDict = {s.name : s.value for s in self.settings}

        year = self.getInt(BD_YEAR) or 1944
        month = self.getInt(BD_MONTH) or 6
        day = self.getInt(BD_DAY) or 6
        print(f"{year}-{month:02}-{day:02}")
        self._BIRTHDAY = date.fromisoformat(f"{year}-{month:02}-{day:02}")

    def getValue(self, name: str) -> Optional[str]:
        """
        Get a string settings value if it exists
        """
        return self._settingsDict.get(name)

    def getInt(self, name: str) -> Optional[int]:
        """
        Get an int settings value, if it exists.
        """
        val = self._settingsDict.get(name)
        return int(val) if val is not None else None


class LegacySettings(BaseXmlModel, tag="Settings"):
    general: list[LegacyGeneralSetting] = element(tag="General",
                                                  default_factory=list)
    user: list[LegacyUserSetting] = element(tag="User",
                                            default_factory=list)


    def getUsers(self) -> list[User]:
        """
        Get the list of users that exist.
        """
        toRet = list[User]()
        userNames = {u.username for u in self.user}
        for user in userNames:
            settings = [s for s in self.user if s.username == user]
            toRet.append(User(username=user, settings=settings))
        return toRet


def loadLegacySettings() -> LegacySettings:
    """
    Load the legacy settings.
    """
    userDir = toolbox.getUserAppDirectory()
    settingsFile = os.path.join(userDir, "Settings.xml")
    with open(settingsFile, 'r') as f:
        return LegacySettings.from_xml(f.read())
