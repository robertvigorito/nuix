"""Convenience helpers for storing application settings with Qt."""

from collections.abc import Mapping
from typing import Any, Optional

from PySide2 import QtCore as _QtCore


class Settings:
    """A small, mapping-like wrapper around :class:`QSettings`.

    Values supplied in ``defaults`` are returned when a key has not been
    persisted yet. Defaults are not written to the settings store until they
    are explicitly written.
    """

    def __init__(
        self,
        organization: Optional[str] = None,
        application: Optional[str] = None,
        defaults: Optional[Mapping[str, Any]] = None,
        settings: Optional[_QtCore.QSettings] = None,
    ) -> None:
        if settings is not None:
            self._settings = settings
        elif organization is None and application is None:
            self._settings = _QtCore.QSettings()
        else:
            self._settings = _QtCore.QSettings(organization or "", application or "")
        self._defaults = dict(defaults or {})

    @property
    def qsettings(self) -> _QtCore.QSettings:
        """Return the underlying Qt settings object."""

        return self._settings

    def read(self, key: str, default: Any = None, value_type: Optional[type] = None) -> Any:
        """Read a value, using configured defaults before ``default``."""

        fallback = self._defaults.get(key, default)
        if value_type is None:
            return self._settings.value(key, fallback)
        return self._settings.value(key, fallback, type=value_type)

    def write(self, key: str, value: Any) -> Any:
        """Persist one value and return it."""

        self._settings.setValue(key, value)
        return value

    def update(self, values: Optional[Mapping[str, Any]] = None, **kwargs: Any) -> None:
        """Persist multiple values and sync them to the backing store."""

        updates = dict(values or {})
        updates.update(kwargs)
        for key, value in updates.items():
            self.write(key, value)
        self._settings.sync()

    def set_default(self, key: str, value: Any) -> None:
        """Set or replace a fallback value without persisting it."""

        self._defaults[key] = value

    def keys(self) -> list[str]:
        """Return persisted keys and configured default keys."""

        return sorted(set(self._settings.allKeys()).union(self._defaults))

    def __contains__(self, key: object) -> bool:
        return key in self._defaults or self._settings.contains(str(key))

    def __getitem__(self, key: str) -> Any:
        value = self.read(key)
        if value is None and key not in self._defaults and not self._settings.contains(key):
            raise KeyError(key)
        return value

    def __setitem__(self, key: str, value: Any) -> None:
        self.write(key, value)


QSettingsExtension = Settings

__all__ = ["Settings", "QSettingsExtension"]
