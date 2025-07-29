"""
Database interface for reading and writing user food servings.
"""
import os

from collections import defaultdict
from datetime import date as dtdate
from typing import Optional

import sqlmodel

from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.engine.base import Engine

import cronometer.util.toolbox as toolbox

from cronometer.foods.food import FoodSource
from cronometer.foods.serving import Serving

DATABASE_NAME = "servings.db"


class SQLServing(Serving, table=True):
    """
    Extension of Serving class that adds an index for keeping
    serving ordering in the database.
    """
    idx: int

    __table_args__ = (PrimaryKeyConstraint("date", "idx"),)


def servingsToSql(servings: list[Serving]) -> list[SQLServing]:
    """
    Add an index field to each serving so it can be writen to
    the database.

    The ordering of the servings in the list is what is used to generate the
    indexes
    """
    return [SQLServing(**serv.model_dump(), idx=idx)
            for idx, serv in enumerate(servings)]


class FoodHistoryDB(object):
    """
    Wrapper class that holds the database connection and provides
    methods for interacting with it.
    """
    def __init__(self, userName: str):
        """
        Create a new instance of the db wrapper.

        There should only be one of these per application or things
        might get pretty wild.
        """
        self.__userName = userName
        dataDir = toolbox.getUserProfileDir(self.__userName)
        self.__dbFile = os.path.join(dataDir, DATABASE_NAME)

        self.__engine = None
        self.__engine = self.__connect()
        sqlmodel.SQLModel.metadata.create_all(self.__engine)

    def __connect(self) -> Engine:
        """
        Clear any existing connection and reconnect
        """
        if self.__engine:
            self.__engine = None
        sqlite_url = f"sqlite:///{self.__dbFile}"
        return sqlmodel.create_engine(sqlite_url)

    def databaseExists(self) -> bool:
        """
        Check if the database file for servings exists
        """
        return os.path.exists(self.__dbFile)

    def reconnect(self):
        """
        Reconnect
        """
        self.__engine = self.__connect()

    def _engine(self) -> Optional[Engine]:
        """
        Access the underlying db engine
        """
        return self.__engine

    def addServings(self, servings: list[Serving]):
        """
        Bulk add a large number of servings.

        This does no duplicate checking, so it should only be used
        for converting legacy servings into the new db format and not
        for modifying existing servings or even adding a new serving.
        """
        servingsByDate = defaultdict(list)

        for s in servings:
            servingsByDate[s.date].append(s)

        with sqlmodel.Session(self.__engine) as session:
            for eachDay in servingsByDate.values():
                session.add_all(servingsToSql(eachDay))
            session.commit()


    def updateDay(self, servings: list[Serving]):
        """
        Remove all servings from the database for the given date and
        replace them with the new list of servings.

        All entries in the servings list must have the same date.
        """
        dateSet = {s.date for s in servings}
        if len(dateSet) != 1:
            raise ValueError("Cannot pass servings from multiple days to updateDay")
        sdate = dateSet.pop()

        with sqlmodel.Session(self.__engine) as session:
            stmt = sqlmodel.select(SQLServing).where(SQLServing.date == sdate)
            for each in session.exec(stmt):
                session.delete(each)
            session.add_all(servingsToSql(servings))
            session.commit()

    def getDay(self, date: dtdate) -> list[Serving]:
        """
        Get all the servings for a given day.

        Return value will be sorted by the internal index which will
        match the list order when the servings were added to the
        database
        """
        stmt = sqlmodel.select(SQLServing).where(SQLServing.date == date)
        with sqlmodel.Session(self.__engine) as session:
            rez = session.exec(stmt)
            return sorted(rez, key=lambda x: x.idx)

    def getConsumptionFrequency(self) -> dict[tuple[FoodSource, int], int]:
        """
        Get the number of times the current user has consumed each food in the
        their servings.

        The key is the source for the food and the UID of the food.
        """
        stmt = sqlmodel.select(SQLServing.source,
                               SQLServing.food,
                               sqlmodel.func.count(SQLServing.idx)).group_by(
                                   SQLServing.source, SQLServing.food)

        toRet = dict[tuple[FoodSource, int], int]()
        with sqlmodel.Session(self.__engine) as session:
            results = session.exec(stmt).all()
            for source, food, count in results:
                toRet[(source, food)] = count

        return toRet


class _FoodHistoryDBDev(FoodHistoryDB):
    """
    Extension of the food history db class for performing testing actions
    """
    def clearServings(self):
        """
        Delete all the serving information in the current db
        """
        stmt = sqlmodel.select(SQLServing)
        with sqlmodel.Session(self._engine()) as session:
            for each in session.exec(stmt):
                session.delete(each)
            session.commit()
