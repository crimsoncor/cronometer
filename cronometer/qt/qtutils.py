"""
Utilities to help with Qt stuff.
"""
from contextlib import contextmanager

from Qt import QtCore
from Qt import QtWidgets


@contextmanager
def blockSignals(*args: QtCore.QObject):
    """
    Contextmanager to block signals for one or more QObject.
    """
    processed = list()
    try:
        processed.extend((e, e.blockSignals(True)) for e in args)
        yield
    finally:
        # Restore the previous state for each object.
        for each, previous in processed:
            each.blockSignals(previous)


@contextmanager
def waitCursor():
    """
    Contextmanager that activates the Qt wait cursor and then deactivates
    it at the end.
    """
    QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
    try:
        yield
    finally:
        QtWidgets.QApplication.restoreOverrideCursor()
