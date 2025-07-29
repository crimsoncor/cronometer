"""
Utilities for working with qt styles.
"""
import os

from Qt import QtGui
from Qt import QtWidgets

THIS_DIR = os.path.abspath(os.path.dirname(__file__))

# FIXME setup style based colors eventually
ICON_COLOR = QtGui.QColorConstants.Svg.midnightblue


def iconDirectory() -> str:
    """
    Get the path to the module directory that holds the icons.
    """
    return os.path.join(THIS_DIR, "icons")


def setupIcon(button: QtWidgets.QAbstractButton, iconName: str):
    """
    Set the icon for the given button
    """
    iconPath = os.path.join(iconDirectory(), iconName)
    icon = colorizeIcon(QtGui.QPixmap(iconPath), ICON_COLOR)
    button.setIcon(icon)


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
