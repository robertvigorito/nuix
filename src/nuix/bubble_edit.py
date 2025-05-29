"""The line_tagger module provides functionality to tag lines in a Nuix case with specific labels."""

import dataclasses as _dataclasses
import re as _re

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
        super().__init__(text, parent)
        content_margins = kwargs.get("content_margins", (0, 0, 0, 0))

        # Set the default values
        padding = kwargs.get("padding", 20)
        self.setFixedHeight(kwargs.get("height", 20))
        # Set the width to wrap the text
        self.setFixedWidth(self.fontMetrics().width(text) + padding)
        self.setContentsMargins(*content_margins)
        # self.setStyleSheet(self.STYLE_SHEET)
        self.setStyleSheet(self.STYLE_SHEET.format(color="rgb(170, 100, 5)", font_color="white", border="0px"))

    @classmethod
    def syntax_label(cls, text="") -> "Bubbles":
        """Create a syntax label with the given text.

        Args:
            text (str, optional): The text to display on the label. Defaults to "".

        Returns:
            TagLabel: The created tag label.
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

    def __init__(self, parent=None, items=None, text="", validator=None, **kwargs) -> None:
        """Initialize the LineEditWithBubbles widget."""
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

    def insert_tag(self, text: str, style: Bubbles) -> bool:
        """Insert a tag with the given text and style.

        Args:
            text (str): The text to display on the tag.
            style (Bubbles): The style of the tag.

        Returns:
            bool: True if the tag was inserted successfully, False otherwise.
        """
        if self.LIMIT and len(self.tags) >= self.LIMIT:
            return False

        label = style(text.strip())
        self.tags.append(label)
        self.layout().addWidget(label)
        self.setTextMargins(self.tags_width(), 0, 0, 0)
        self.setText(self.text().replace(text, "").strip())

        return True

    def keyPressEvent(self, event) -> None:
        # Remove the last bubble if backspace is pressed
        if event.key() == _QtCore.Qt.Key_Backspace and self.tags and not self.text():
            self.tags.pop().deleteLater()
            self.setTextMargins(self.tags_width(), 0, 0, 0)
            return None
        # Order of the super matter when handling text conversion to bubbles.
        super().keyPressEvent(event)
        # Cross cheeck to the limit of the tags
        if self.LIMIT and len(self.tags) >= self.LIMIT:
            return None
        for split_text in _re.split(self.SEPARATOR, self.text()) or [self.text()]:
            if split_text not in self.complete_items or split_text in self.tag_names():
                continue
            self.insert_tag(split_text, Bubbles)

        # Add the syntax label if the text is a valid syntax
        separator_match = _re.findall(self.SEPARATOR, self.text())
        if self.text() and separator_match:
            bubble = Bubbles.plain_label
            if self.text() == separator_match[-1]:
                bubble = Bubbles.syntax_label
            self.insert_tag(self.text(), bubble)

        self.editing_finished_trigger()

        return None

    def editing_finished_trigger(self) -> bool:
        """If we have tags in the line edit we should allow for separators to be used

        Returns:
            bool: True if the editing finished, False otherwise.
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
    """The class is a container of the widget to reduce the noise of py when interacting with the class."""

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

    def __contains__(self, item: str) -> bool:
        """Check if the item is in the tags.

        Args:
            item (str): The item to check.

        Returns:
            bool: True if the item is in the tags, False otherwise.
        """
        return item in self.get_tags()


class DropDownTagger(_QtWidgets.QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.form_layout = _QtWidgets.QFormLayout()
        self.setLayout(self.form_layout)

        tag = BubbleWrap(items=["apple", "banana", "cherry", "date", "elderberry", "fig", "grape", "Honeydew"], limit=0)

        self.form_layout.addRow("Labels", tag.widget)
        self.delete_me()

    def delete_me(self):
        self.setGeometry(0, 0, 300, 200)
        screen = _QtWidgets.QApplication.primaryScreen()
        screen_size = screen.size()
        window_size = self.size()
        x = (screen_size.width() - window_size.width()) / 2
        y = (screen_size.height() - window_size.height()) / 2 - 300
        self.move(x, y)


if __name__ == "__main__":
    import sys

    app = _QtWidgets.QApplication(sys.argv)
    window = DropDownTagger()
    window.show()
    sys.exit(app.exec_())
