"""Tests for the LineEditWithBubbles widget."""

import pytest
from PySide2 import QtCore

from nuix.bubble_edit import LineEditWithBubbles

BUBBLE_ITEMS = ["apple", "banana", "cherry", "date"]


@pytest.fixture(name="bubble_line_edit")
def bubble_line_edit_fixture(qtbot):
    """Fixture for the LineEditWithBubbles widget.

    Creates a LineEditWithBubbles widget with predefined items and adds it to the QtBot for testing.
    """
    line_edit = LineEditWithBubbles(items=BUBBLE_ITEMS, limit=5)
    qtbot.addWidget(line_edit)
    return line_edit


def test_insert_tag(qtbot, bubble_line_edit):
    """Test inserting tags into the LineEditWithBubbles widget."""
    line_edit = bubble_line_edit

    # Insert a valid tag
    assert line_edit.insert_tag("apple"), "Tag should be inserted successfully"
    assert "apple" in line_edit.tag_names(), "Tag name should be present in the list of tags"

    # Insert another valid tag
    assert line_edit.insert_tag("banana"), "Tag should be inserted successfully"
    assert "banana" in line_edit.tag_names(), "Tag name should be present in the list of tags"

    # Exceed the limit
    for _ in range(3):
        line_edit.insert_tag("extra")
    assert not line_edit.insert_tag("overflow"), "Tag insertion should fail when limit is exceeded"


def test_key_press_event(qtbot, bubble_line_edit):
    """Test handling key press events in the LineEditWithBubbles widget."""
    line_edit = bubble_line_edit

    # Insert a tag and simulate backspace key press
    line_edit.insert_tag("apple")
    assert "apple" in line_edit.tag_names(), "Tag name should be present in the list of tags"

    qtbot.keyPress(line_edit, QtCore.Qt.Key_Backspace)
    assert "apple" not in line_edit.tag_names(), "Tag should be removed after backspace key press"


def test_tag_names(qtbot, bubble_line_edit):
    """Test retrieving tag names from the LineEditWithBubbles widget."""
    line_edit = bubble_line_edit

    # Insert multiple tags
    line_edit.insert_tag("apple")
    line_edit.insert_tag("banana")

    assert line_edit.tag_names() == ["apple", "banana"], "Tag names should match the inserted tags"


def test_tags_width(qtbot, bubble_line_edit):
    """Test calculating the total width of tags in the LineEditWithBubbles widget."""
    line_edit = bubble_line_edit

    # Insert multiple tags
    line_edit.insert_tag("apple")
    line_edit.insert_tag("banana")

    assert line_edit.tags_width() > 0, "Tags width should be greater than zero"


def test_bubble_limit(qtbot, bubble_line_edit):
    """Test the limit on the number of tags in the LineEditWithBubbles widget."""
    line_edit = bubble_line_edit
    line_edit.LIMIT = 2

    for item in BUBBLE_ITEMS:
        # Add the test with qtbot to simulate user interaction
        qtbot.keyClicks(line_edit, item)

    # Check that only the first two items are added
    assert len(line_edit.tags) == 2, "Only two tags should be allowed due to the limit"
    assert "apple" in line_edit.tag_names(), "First tag should be apple"

    assert "banana" in line_edit.tag_names(), "Second tag should be banana"


def test_plain_syntax_bubbles(qtbot, bubble_line_edit):

    # Add first tag with syntax label
    qtbot.keyClicks(bubble_line_edit, "apple")

    qtbot.keyClicks(bubble_line_edit, "_")

    qtbot.keyClicks(bubble_line_edit, "textwithsyntax_")

    # There should be three tags now: "apple", "_", "textwithsyntax_"
    assert bubble_line_edit.tag_names() == [
        "apple",
        "_",
        "textwithsyntax_",
    ], "Tags should include the syntax label and plain text"


def test_bubble_width_measurements(qtbot, bubble_line_edit):
    """Test the width measurements of the bubbles in the LineEditWithBubbles widget."""
    line_edit = bubble_line_edit

    # Insert a tag and check its width
    line_edit.insert_tag("apple")
    assert line_edit.tags_width() > 0, "Tags width should be greater than zero after inserting a tag"

    # Check if the width is calculated correctly
    initial_width = line_edit.tags_width()
    line_edit.insert_tag("banana")
    assert line_edit.tags_width() > initial_width, "Tags width should increase after adding another tag"
