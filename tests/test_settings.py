"""Tests for the QSettings convenience wrapper."""

from qtpy import QtCore

from nuix import Settings


def test_read_uses_defaults_without_persisting(qtbot, tmp_path):
    settings = QtCore.QSettings(str(tmp_path / "settings.ini"), QtCore.QSettings.IniFormat)
    wrapper = Settings(defaults={"theme": "dark"}, settings=settings)

    assert wrapper.read("theme") == "dark"
    assert not settings.contains("theme")


def test_write_and_update_persist_values(qtbot, tmp_path):
    settings = QtCore.QSettings(str(tmp_path / "settings.ini"), QtCore.QSettings.IniFormat)
    wrapper = Settings(settings=settings)

    wrapper.write("enabled", True)
    wrapper.update({"count": 2}, name="nuix")

    assert wrapper.read("enabled", value_type=bool) is True
    assert wrapper["count"] == 2
    assert set(wrapper.keys()) == {"count", "enabled", "name"}
    assert wrapper.get_all() == {"count": 2, "enabled": True, "name": "nuix"}
    assert [record.key for record in wrapper.get_all_records()] == ["count", "enabled", "name"]


def test_missing_item_behaves_like_mapping(qtbot, tmp_path):
    settings = QtCore.QSettings(str(tmp_path / "settings.ini"), QtCore.QSettings.IniFormat)
    wrapper = Settings(settings=settings)

    assert "missing" not in wrapper
    try:
        wrapper["missing"]
    except KeyError as error:
        assert error.args == ("missing",)
    else:
        raise AssertionError("Missing settings should raise KeyError")
