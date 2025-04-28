"""
Utilities for working with qt styles.
"""
import os

from Qt import QtGui

THIS_DIR = os.path.abspath(os.path.dirname(__file__))


def iconDirectory() -> str:
    """
    Get the path to the module directory that holds the icons.
    """
    return os.path.join(THIS_DIR, "icons")


def colorizePixmap(pixmap: QtGui.QPixmap, color: QtGui.QColor) -> QtGui.QPixmap:
    """
    Create a new pixmap by applying the given color to the given pixmap.
    """
    copied = pixmap.copy()
    painter = QtGui.QPainter(copied)
    painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceIn)
    painter.fillRect(copied.rect(), color)
    painter.end()
    return copied


def colorizeIcon(pixmap: QtGui.QPixmap, color: QtGui.QColor) -> QtGui.QIcon:
    """
    Create a new icon by applying the given color to the given pixmap
    """
    return QtGui.QIcon(colorizePixmap(pixmap, color))
