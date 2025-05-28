"""Custom line edit widget for Nuix."""

# pyright: disable=too-few-public-methods

from PySide2 import QtCore as _QtCore
from PySide2 import QtGui as _QtGui
from PySide2 import QtWidgets as _QtWidgets


class LineEditValidator(_QtWidgets.QLineEdit):  # pylint: disable=too-few-public-methods
    """The line edit with a validator."""

    VALIDATOR_PATTERN = r"[a-zA-Z]+[a-zA-Z0-9_]+"

    def __init__(self, parent=None, text="", validator=None) -> None:
        """The initiation method.

        Args:
            parent ([type], optional): The parent widget. Defaults to None.
            text (str, optional): The text to display on the line edit. Defaults to "".
        """
        super().__init__(parent)
        self.setText(str(text))
        self.setValidator(_QtGui.QRegExpValidator(validator or self.VALIDATOR_PATTERN))  # type: ignore
        self.setClearButtonEnabled(True)


class LineEditWithCompleter(LineEditValidator):
    """The line edit supports an inline completer and a popup completer.

    Unfortunately, the default completer can only support one and this class provides both options.
    """

    def __init__(self, parent=None, text="", items=None, validator=None) -> None:
        """The initiation method.

        Args:
            parent ([type], optional): The parent widget. Defaults to None.
            text (str, optional): The text to display on the line edit. Defaults to "".
            items ([type], optional): The items to display in the completer. Defaults to None.
        """
        super().__init__(parent)
        self.complete_items = items or []
        # Needs to be the first line or the overwritten setText will not work
        self.setText(str(text))
        self.setCompleter(_QtWidgets.QCompleter())
        self.completer().setModel(_QtCore.QStringListModel(self.complete_items))
        self.setValidator(_QtGui.QRegExpValidator(validator or self.VALIDATOR_PATTERN))  # type: ignore

    def keyPressEvent(self, event) -> None:  # pylint: disable=invalid-name
        """The key press event handler - Show the popup completer.

        Args:
            event (QKeyEvent): The key event.
        """
        if event.key() in [_QtCore.Qt.Key_Backspace] and self.text():
            self.blockSignals(True)
            # Remove the selected text
            self.setText(self.text().replace(self.selectedText(), ""))
            super().keyPressEvent(event)
            self.blockSignals(False)
            return None

        if self.completer() and not self.completer().popup().isVisible() and event.key() != _QtCore.Qt.Key_Enter:
            self.completer().setCompletionPrefix(self.text())
            self.completer().complete()
            # If there are suggestions, show the popup
            if self.completer().completionCount():
                self.completer().popup().show()
        if event.key() in [_QtCore.Qt.Key_Up, _QtCore.Qt.Key_Down] and self.text().isdigit():
            value = 1 if event.key() == _QtCore.Qt.Key_Up else -1
            self.setText(str(int(self.text()) + value))

        super().keyPressEvent(event)

        return None


class LineEditWithInlineCompleter(LineEditWithCompleter):
    """The line edit with an inline completer.

    This class is used to provide an inline completer that shows suggestions as the user types.
    """

    def __init__(self, parent=None, text="", items=None, validator=None) -> None:
        """The initiation method.

        Args:
            parent ([type], optional): The parent widget. Defaults to None.
            text (str, optional): The text to display on the line edit. Defaults to "".
            items ([type], optional): The items to display in the completer. Defaults to None.
        """
        super().__init__(parent, text, items, validator)

        self.textEdited.connect(self.activate_inline_complete)

    def activate_inline_complete(self):
        """The method to auto complete the text inline.

        Returns:
            bool: True if the text has been auto completed, False otherwise.
        """
        # Set the completion prefix
        self.completer().setCompletionPrefix(self.text())
        # Get the closest match from the completion model
        completion_model = self.completer().completionModel()
        if completion_model.rowCount() < 0 or self.text().isdigit():
            return False

        closest_match = completion_model.index(0, 0).data()
        # Display hint text inline by showing the rest of the closest match in a subtle way
        typed_text = self.text()
        if closest_match and closest_match.startswith(typed_text):
            hint_text = closest_match[len(typed_text) :]  # Get only the hint part of the completion
            self.setText(typed_text + hint_text)
            # Select the hint part to indicate it's a suggestion
            self.setSelection(len(typed_text), len(hint_text))

        return True

    def keyPressEvent(self, event):
        """The key press event handler - Show the inline completer.

        Args:
            event (QKeyEvent): The key event.

        Returns:
            None: No return value.
        """
        if event.key() in [_QtCore.Qt.Key_Enter, _QtCore.Qt.Key_Return]:
            # If the user pressed enter, try to auto complete the text inline
            self.activate_inline_complete()
        return super().keyPressEvent(event)
