"""The line_tagger module provides functionality to tag lines in a Nuix case with specific labels."""

import dataclasses as _dataclasses
import re as _re
import typing as _typing

from PySide2 import QtCore as _QtCore
from PySide2 import QtGui as _QtGui
from PySide2 import QtWidgets as _QtWidgets

from nuix.lineedit import LineEditWithCompleter as _LineEditWithCompleter


class Bubbles(_QtWidgets.QPushButton):
    """A widget that displays bubbles for editing text with inline completion."""

    STYLE_SHEET = """
        QPushButton:hover {{ background-color: rgb(230, 130, 10); }}
        QPushButton {{border-radius: 4px; background-color: {color}; border: {border}; padding: 0px; margin: 0px; font-weight: none; font-size: 12px; color: {font_color};}}
    """

    def __init__(self, text="", parent=None, **kwargs) -> None:
        """Initialize the Bubbles widget.

        Args:
            text (str, optional): The text to display on the bubble. Defaults to "".
            parent (QWidget, optional): The parent widget. Defaults to None.
            **kwargs: Additional keyword arguments for customization.
        """
        super().__init__(text, parent)
        content_margins = kwargs.get("content_margins", (0, 0, 0, 0))

        # Set the default values
        padding = kwargs.get("padding", 20)
        self.setFixedHeight(kwargs.get("height", 20))
        # Use horizontalAdvance instead of width to calculate text width
        self.setFixedWidth(self.fontMetrics().horizontalAdvance(text) + padding)
        self.setContentsMargins(*content_margins)
        self.setStyleSheet(self.STYLE_SHEET.format(color="rgb(170, 100, 5)", font_color="white", border="0px"))

    @classmethod
    def syntax_label(cls, text="") -> "Bubbles":
        """Create a syntax label with the given text.

        Args:
            text (str, optional): The text to display on the label. Defaults to "".

        Returns:
            Bubbles: The created syntax label.
        """
        syntax_label = cls(text)
        # Make the color light purple
        syntax_label.setStyleSheet(cls.STYLE_SHEET.format(color="rgb(200, 150, 250)", font_color="white", border="0px"))
        return syntax_label

    @classmethod
    def plain_label(cls, text="") -> "Bubbles":
        """Create a plain label with no color background.

        Args:
            text (str, optional): The text to display on the label. Defaults to "".

        Returns:
            Bubbles: The created plain label.
        """
        plain_label = cls(text)
        # Make the color light purple
        plain_label.setStyleSheet(
            cls.STYLE_SHEET.format(color="transparent", font_color="black", border="1px solid black")
        )

        return plain_label


class LineEditWithBubbles(_LineEditWithCompleter):
    """A line edit widget that supports bubble editing with inline completion.

    This widget extends the LineEditWithCompleter to allow for bubble editing functionality.
    """

    SEPARATOR = "[_]"
    TAG_PADDING = 2  # Padding between tags
    LIMIT = -1  # Default limit for the number of tags, -1 means no limit

    def __init__(self, parent=None, items=None, text="", validator=None, **kwargs) -> None:
        """Initialize the LineEditWithBubbles widget.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
            items (list[str], optional): List of items for completion. Defaults to None.
            text (str, optional): Initial text for the widget. Defaults to "".
            validator (QValidator, optional): Validator for the input. Defaults to None.
            **kwargs: Additional keyword arguments for customization.
        """
        super().__init__(parent, items=items, text=text, validator=validator)
        self.LIMIT = kwargs.get("limit", 10)  # Maximum number of tags allowed
        self.tags: list[Bubbles] = []
        # Set the layout to a horizontal layout
        self.setLayout(_QtWidgets.QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(self.TAG_PADDING)
        # Set the alignment of the layout to the left
        self.layout().setAlignment(_QtCore.Qt.AlignLeft)

        # Clear the text once the complete does its job
        self.completer().activated.connect(lambda: _QtCore.QTimer.singleShot(0, self.clear))
        self.editingFinished.connect(self.editing_finished_trigger)

    def get_syntax_label(self, text: str) -> _typing.Optional[Bubbles]:
        """Get a syntax label with the given text.

        Args:
            text (str): The text to display on the label.

        Returns:
            Optional[Bubbles]: The created syntax label or None if invalid.
        """
        text = text.strip() or self.text().strip()
        if not text:
            return None
        # Check if the limit of tags has been reached
        if self.LIMIT > 0 and len(self.tags) >= self.LIMIT:
            return None

        # Split the text using the separator and validate each part
        for split_text in _re.split(self.SEPARATOR, text):
            split_text = split_text.strip()
            if not split_text or split_text in self.tag_names() or split_text not in self.complete_items:
                continue
            return Bubbles(text=split_text)
        if _re.findall(self.SEPARATOR, text):
            if text in self.SEPARATOR:
                return Bubbles.syntax_label(text=text.strip())
            return Bubbles.plain_label(text=text.strip())
        return None

    def insert_tag(self, text: str) -> bool:
        """Insert a tag with the given text.

        Args:
            text (str): The text to display on the tag.

        Returns:
            bool: True if the tag was inserted successfully, False otherwise.
        """
        if not text:
            return False
        if not text or (self.LIMIT and len(self.tags) >= self.LIMIT):
            return False
        # Check if the text is empty or already exists in the tags
        label = self.get_syntax_label(text)
        if not label:
            return False

        self.tags.append(label)
        self.layout().addWidget(label)
        self.setTextMargins(self.tags_width(), 0, 0, 0)
        self.setText(self.text().replace(text, "").strip())

        return True

    def keyPressEvent(self, event) -> None:
        """Handle key press events to manage bubble editing.

        Args:
            event (QKeyEvent): The key press event.
        """
        # Remove the last bubble if backspace is pressed
        if event.key() == _QtCore.Qt.Key_Backspace and self.tags and not self.text():
            self.tags.pop().deleteLater()
            self.setTextMargins(self.tags_width(), 0, 0, 0)
            return None
        # Order of the super matter when handling text conversion to bubbles.
        super().keyPressEvent(event)
        # Handle the tag insertion.
        self.insert_tag(self.text().strip())
        # Dont remove, required to allow separators to be used if there is a tag in the line edit.
        self.editing_finished_trigger()

        return None

    def editing_finished_trigger(self) -> bool:
        """Update the validator pattern based on the presence of tags.

        Returns:
            bool: True if the editing finished successfully.
        """
        validation_string = self.VALIDATOR_PATTERN

        if self.tags:
            validation_string = f"{self.SEPARATOR}?" + self.VALIDATOR_PATTERN

        self.setValidator(_QtGui.QRegExpValidator(validation_string))  # type: ignore

        return True

    def tag_names(self) -> list[str]:
        """Get the names of the tags.

        Returns:
            list[str]: The list of tag names.
        """
        return [tag.text() for tag in self.tags if tag.text()]

    def tags_width(self) -> int:
        """Get the total width of the tags.

        Returns:
            int: The total width of the tags.
        """
        return sum(tag.width() + self.TAG_PADDING for tag in self.tags)


@_dataclasses.dataclass(eq=True, order=True)
class BubbleWrap:
    """A container class for managing the LineEditWithBubbles widget.

    Example:
        >>> bubble_wrap = BubbleWrap(items=["apple", "banana", "cherry"], limit=5, text="Initial text")
        >>> bubble_wrap.set_text("New tag")
        >>> print(bubble_wrap.get_tags())
        >>> print(bubble_wrap.join_tags(separator=", "))
    

    Args:
        items (list[str], optional): List of items for the bubble editor. Defaults to an empty list.
        limit (int, optional): Maximum number of tags allowed. Defaults to 10.
        text (str, optional): Initial text for the bubble editor. Defaults to an empty string.
        validator (str, optional): Validator pattern for the input. Defaults to an empty string.

    Attributes:
        items (list[str]): List of items for the bubble editor.
        limit (int): Maximum number of tags allowed.
        text (str): Initial text for the bubble editor.
        validator (str): Validator pattern for the input.
        widget (LineEditWithBubbles): The LineEditWithBubbles widget instance.
    """

    items: list[str] = _dataclasses.field(default_factory=list)
    limit: int = _dataclasses.field(default=10)
    text: str = _dataclasses.field(default="")
    validator: str = _dataclasses.field(default="")

    widget: LineEditWithBubbles = _dataclasses.field(default_factory=LineEditWithBubbles)

    def __post_init__(self) -> None:
        """Post-initialization to set the items and limit for the widget."""
        self.widget = LineEditWithBubbles(
            parent=None, items=self.items, text=self.text, validator=self.validator, limit=self.limit
        )

    def get_tags(self) -> list[str]:
        """Get the tags from the widget.

        Returns:
            list[str]: The list of tags.
        """
        return self.widget.tag_names()

    def get_text(self) -> str:
        """Get the text from the widget.

        Returns:
            str: The text from the widget.
        """
        return self.widget.text().strip()

    def join_tags(self, separator="") -> str:
        """Get the tags as a joined string.

        Args:
            separator (str, optional): The separator to use between tags. Defaults to "".

        Returns:
            str: The joined tags string.
        """
        return separator.join(self.get_tags()) + self.widget.text().strip()

    def set_text(self, text: str) -> bool:
        """Set the text in the widget.

        Args:
            text (str): The text to set in the widget.

        Returns:
            bool: True if the tag was inserted successfully, False otherwise.
        """
        self.widget.setText(text.strip())
        return self.widget.insert_tag(text.strip())

    def __contains__(self, item: str) -> bool:
        """Check if the item is in the tags.

        Args:
            item (str): The item to check.

        Returns:
            bool: True if the item is in the tags, False otherwise.
        """
        return item in self.get_tags()


# class DropDownTagger(_QtWidgets.QWidget):
#     def __init__(self, parent=None) -> None:
#         super().__init__(parent)

#         self.form_layout = _QtWidgets.QFormLayout()
#         self.setLayout(self.form_layout)

#         self.tag = BubbleWrap(
#             items=["apple", "banana", "cherry", "date", "elderberry", "fig", "grape", "Honeydew"], limit=0
#         )

#         self.form_layout.addRow("Labels", self.tag.widget)
#         self.delete_me()

#     def delete_me(self):
#         self.setGeometry(0, 0, 300, 200)
#         screen = _QtWidgets.QApplication.primaryScreen()
#         screen_size = screen.size()
#         window_size = self.size()
#         x = (screen_size.width() - window_size.width()) / 2
#         y = (screen_size.height() - window_size.height()) / 2 - 300
#         self.move(x, y)


# if __name__ == "__main__":
#     import sys

#     app = _QtWidgets.QApplication(sys.argv)
#     window = DropDownTagger()
#     window.show()
#     window.tag.set_text("banana")
#     window.tag.set_text("banana_")
#     window.tag.set_text("_")
#     sys.exit(app.exec_())
