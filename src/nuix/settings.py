"""Convenience helpers for storing application settings with Qt.

``Settings`` provides a small, mapping-like API around ``QSettings`` while
keeping application defaults in one place. Values can be saved individually,
as a dictionary, or from a dataclass.

For example, a form widget can restore its fields when it opens and save them
when it closes::

    from dataclasses import dataclass

    from qtpy import QtWidgets

    from nuix.settings import Settings


    @dataclass
    class FormValues:
        name: str = ""
        email: str = ""


    class ProfileForm(QtWidgets.QWidget):
        def __init__(self):
            super().__init__()
            self.settings = Settings(
                organization="Example",
                application="ProfileForm",
                defaults={"name": "", "email": ""},
            )
            self.name_edit = QtWidgets.QLineEdit()
            self.email_edit = QtWidgets.QLineEdit()
            layout = QtWidgets.QFormLayout(self)
            layout.addRow("Name", self.name_edit)
            layout.addRow("Email", self.email_edit)
            self.restore_form()

        def restore_form(self):
            values = self.settings.get(FormValues)
            self.name_edit.setText(values.name)
            self.email_edit.setText(values.email)

        def closeEvent(self, event):
            self.settings.save(
                FormValues(
                    name=self.name_edit.text(),
                    email=self.email_edit.text(),
                )
            )
            event.accept()
"""

from collections.abc import Mapping
from dataclasses import MISSING, asdict, dataclass, fields, is_dataclass

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
        defaults: object = None,
        settings: _QtCore.QSettings = None,
    ) -> None:
        if settings is not None:
            self._settings = settings
        elif organization is None and application is None:
            self._settings = _QtCore.QSettings()
        else:
            self._settings = _QtCore.QSettings(organization or "", application or "")
        self._defaults = self._as_mapping(defaults)

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

    def get(self, model: type) -> object:
        """Load a dataclass using its field names as settings keys.

        This avoids repeating string keys at call sites::

            values = settings.get(FormValues)
            self.name_edit.setText(values.name)
        """

        if not isinstance(model, type) or not is_dataclass(model):
            raise TypeError("model must be a dataclass type")
        values = {}
        for field in fields(model):
            default = self._defaults.get(field.name, MISSING)
            if default is MISSING:
                default = field.default
            if default is MISSING and field.default_factory is not MISSING:
                default = field.default_factory()
            value_type = field.type if isinstance(field.type, type) else None
            values[field.name] = self.read(field.name, None if default is MISSING else default, value_type)
        return model(**values)

    load = get

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

    def __setitem__(self, key: str, value: object) -> None:
        self.write(key, value)


QSettingsExtension = Settings

__all__ = ["Setting", "Settings", "QSettingsExtension"]
