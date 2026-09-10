"""Convenience helpers for storing application settings with Qt."""

from collections.abc import Mapping
from dataclasses import asdict, dataclass, is_dataclass

from qtpy import QtCore as _QtCore


@dataclass(frozen=True)
class Setting:
    """A named setting value returned by :meth:`Settings.get_all_records`."""

    key: str
    value: object


class Settings:
    """A small, mapping-like wrapper around :class:`QSettings`.

    Values supplied in ``defaults`` are returned when a key has not been
    persisted yet. Defaults are not written to the settings store until they
    are explicitly written.
    """

    def __init__(
        self,
        organization: str = None,
        application: str = None,
        defaults: Mapping[str, object] = None,
        settings: _QtCore.QSettings = None,
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

    def read(self, key: str, default: object = None, value_type: type = None) -> object:
        """Read a value, using configured defaults before ``default``."""

        fallback = self._defaults.get(key, default)
        if value_type is None:
            return self._settings.value(key, fallback)
        return self._settings.value(key, fallback, type=value_type)

    def write(self, key: str, value: object) -> object:
        """Persist one value and return it."""

        self._settings.setValue(key, value)
        return value

    @staticmethod
    def _as_mapping(values: object = None) -> dict[str, object]:
        if values is None:
            return {}
        if is_dataclass(values) and not isinstance(values, type):
            return asdict(values)
        if isinstance(values, Mapping):
            return dict(values)
        raise TypeError("values must be a mapping or dataclass instance")

    def update(self, values: object = None, **kwargs: object) -> None:
        """Persist multiple mapping or dataclass values and sync the store."""

        updates = self._as_mapping(values)
        updates.update(kwargs)
        for key, value in updates.items():
            self.write(key, value)
        self._settings.sync()

    def save(self, values: object) -> None:
        """Persist a dictionary or dataclass instance and sync the store."""

        self.update(values)

    def set_default(self, key: str, value: object) -> None:
        """Set or replace a fallback value without persisting it."""

        self._defaults[key] = value

    def keys(self) -> list[str]:
        """Return persisted keys and configured default keys."""

        return sorted(set(self._settings.allKeys()).union(self._defaults))

    def get_all(self) -> dict[str, object]:
        """Return all persisted settings, supplemented by configured defaults."""

        return {key: self.read(key) for key in self.keys()}

    def get_all_records(self) -> list[Setting]:
        """Return all settings as immutable dataclass records."""

        return [Setting(key, value) for key, value in self.get_all().items()]

    def __contains__(self, key: object) -> bool:
        return key in self._defaults or self._settings.contains(str(key))

    def __getitem__(self, key: str) -> object:
        value = self.read(key)
        if value is None and key not in self._defaults and not self._settings.contains(key):
            raise KeyError(key)
        return value

    def __setitem__(self, key: str, value: Any) -> None:
        self.write(key, value)


QSettingsExtension = Settings

__all__ = ["Setting", "Settings", "QSettingsExtension"]
