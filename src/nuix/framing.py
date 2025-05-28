"""The module holds custom framing widgets for Nuix.
"""

from PySide2 import QtWidgets as _QtWidgets


class HorizontalLine(_QtWidgets.QFrame):  # pylint: disable=too-few-public-methods
    """The horizontal line widget."""

    def __init__(self, parent=None) -> None:
        """The initiation method.

        Args:
            parent ([type], optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.setFrameShape(_QtWidgets.QFrame.HLine)
        self.setFrameShadow(_QtWidgets.QFrame.Sunken)
