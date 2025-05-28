"""Test that the line edits are working as expected."""

import pytest
from PySide2 import QtCore

from nuix.lineedit import LineEditValidator, LineEditWithCompleter, LineEditWithInlineCompleter  # type: ignore


@pytest.fixture(name="validation_line_edit")
def standard_line_edit_validator(qtbot):
    """Fixture for the line edit validator.

    Creates a LineEditValidator widget and adds it to the QtBot for testing.
    """
    # Create the standard line edit validator
    line_edit = LineEditValidator()
    qtbot.addWidget(line_edit)
    return line_edit


@pytest.fixture(name="inline_validation_line_edit")
def standard_inline_line_edit_validator(qtbot):
    """Fixture for the line edit with an inline completer.

    Creates a LineEditWithInlineCompleter widget with predefined items and adds it to the QtBot for testing.
    """
    # Define items for the inline completer
    items = ["apple", "banana", "cherry", "date"]
    line_edit = LineEditWithInlineCompleter(items=items)
    qtbot.addWidget(line_edit)
    return line_edit


@pytest.mark.parametrize(
    "text, result",
    [
        ("valid_text", "valid_text"),  # Valid input should remain unchanged
        ("invalid text", "invalidtext"),  # Spaces should be removed
        ("123_invalid", "invalid"),  # Numbers at the start should be removed
        ("valid_text_123", "valid_text_123"),  # Valid input with numbers at the end should remain unchanged
        ("_", ""),  # Underscore alone should result in an empty string
    ],
)
def test_the_pattern_validator(qtbot, validation_line_edit: LineEditValidator, text, result):
    """Test the LineEditValidator for various input patterns.

    Ensures that the validator correctly modifies the input text based on predefined rules.
    """
    # Simulate typing the text into the line edit
    qtbot.keyClicks(validation_line_edit, text)

    # Assert that the text matches the expected result
    assert validation_line_edit.text() == result, f"Text should match the provided result {validation_line_edit.text()}"


def test_auto_complete_line_edit(qtbot):
    """Test the LineEditWithCompleter widget.

    Verifies that the completer correctly handles item selection, filtering, and text modification.
    """
    # Define items for the completer
    items = ["item1", "item2", "item3"]
    line_edit = LineEditWithCompleter(items=items)
    qtbot.addWidget(line_edit)

    # Check that the completer contains all items
    assert line_edit.completer().completionCount() == len(items), "Completer should have all items"

    # Simulate typing to select an item
    qtbot.keyClicks(line_edit, "item2")
    assert line_edit.completer().currentCompletion() == "item2", "First item should be selected by default"

    # Verify the completer still contains all items
    assert line_edit.completer().completionCount() == 1, "Completer should have all items"

    # Test clearing the text
    line_edit.selectAll()
    qtbot.keyPress(line_edit, QtCore.Qt.Key_Backspace)
    assert line_edit.text() == "", "Text should be empty after backspace"

    # Test typing a new item
    qtbot.keyClicks(line_edit, "item1")
    assert line_edit.text() == "item1", "Text should match the selected item from the completer"


def test_inline_auto_complete_line_edit(qtbot, inline_validation_line_edit: LineEditWithInlineCompleter):
    """Test the LineEditWithInlineCompleter widget.

    Verifies that the inline completer correctly handles item selection, filtering, and text modification.
    """
    # Use the fixture-provided inline completer
    items = ["apple", "banana", "cherry", "date"]
    line_edit = inline_validation_line_edit
    qtbot.addWidget(line_edit)

    # Check that the completer contains all items
    assert line_edit.completer().completionCount() == len(items), "Completer should have all items"

    # Simulate typing to filter items
    qtbot.keyClicks(line_edit, "ba")
    assert line_edit.completer().currentCompletion() == "banana", "First item should be selected by default"
    assert line_edit.completer().completionCount() == 1, "Completer should have filtered items"

    # Test clearing the text
    line_edit.selectAll()
    qtbot.keyPress(line_edit, QtCore.Qt.Key_Backspace)
    assert line_edit.text() == "", "Text should be empty after backspace"

    # Test typing and selecting another item
    qtbot.keyClicks(line_edit, "ch")
    assert line_edit.text() == "cherry", "Text should match the typed text"

    # Test inline completion with key press
    qtbot.keyPress(line_edit, QtCore.Qt.Key_Backspace)  # Remove last character
    qtbot.keyPress(line_edit, QtCore.Qt.Key_Return)  # Confirm auto-completion
    assert line_edit.text() == "cherry", "Text should be auto completed to the closest match"
