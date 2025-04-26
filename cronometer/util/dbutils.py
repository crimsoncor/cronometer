"""
Utility functions to help with using sqlite3
"""
import sqlite3


def tableExist(cur: sqlite3.Cursor, name: str) -> bool:
    """
    Check if a table already exists in the database.
    """
    cmd = 'SELECT EXISTS(SELECT 1 FROM sqlite_master WHERE type="table" AND name="{}");'
