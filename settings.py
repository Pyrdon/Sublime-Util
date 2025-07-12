import logging

# Local _logger
_logger = logging.getLogger(__name__)

import sublime

from .validators import *
from . import status

class Settings():
    def __init__(self):
        self._settings = SettingsList()

    def init(self, default_log_level, log_level_callback):
        self._settings_file = sublime.load_settings(f"{__name__.split('.')[0]}.sublime-settings")
        self._settings_file.add_on_change(__package__, self._on_settings_change)

        self._settings.add(LogLevelSetting('log_level', default_log_level))
        self.log_level.add_on_change(__package__, log_level_callback)

        # Call this once on creation to set it up
        self._on_settings_change()

    def deinit(self):
        _logger.debug("Deleting settings.")
        self._settings_file.clear_on_change(__package__)
        self.log_level.clear_on_change(__package__)

    def __getattr__(self, name):
        if not name.startswith("_"):
            try:
                return self._settings[name]
            except KeyError as e:
                raise NameError(f"No such setting '{name}'.") from None

    def _on_settings_change(self):
        _logger.debug("Reloading settings.")
        for name, setting in self._settings.items():
            try:
                setting._update(self._settings_file[name])
            except KeyError as e:
                setting._set_default()

        # Find all settings in settings file but not defined by the plugin
        diff = list(set(self._settings_file.to_dict().keys()) - set(self._settings.keys()))
        if diff:
            if len(diff) == 1:
                status.error_message(f"Unknown setting '{diff[0]}'.")
            else:
                status.error_message(f"Unknown settings {diff}.")

class SettingsList(dict):
    # def __init__(self):
    #     self._settings = {}

    def add(self, setting):
        self[setting._name] = setting
        # self._settings[setting._name] = setting

class SingleSetting():
    def __init__(self, name, value, validator):
        self._name = name
        self._value = None
        self._default = value
        self._validator = validator
        self._callbacks = {}
        self._update(str(value))

    def __str__(self):
        return str(self.value)

    def __bool__(self):
        return bool(self.value)

    @property
    def value(self):
        return self._value

    def validate(self, value):
        return self._validator.validate(value)

    def add_on_change(self, tag, callback):
        try:
            self._callbacks[tag]
        except KeyError as e:
            _logger.debug(f"Adding callback '{tag}' for setting '{self._name}'.")
            self._callbacks[tag] = callback
        else:
            raise ValueError(
                f"Tag '{tag}' already registered a callback for change of setting '{self._name}'.") from None

    def clear_on_change(self, tag):
        try:
            self._callbacks[tag]
        except KeyError as e:
            raise ValueError(
                f"Tag '{tag}' not registered a callback for change of setting '{self._name}'.") from None
        else:
            _logger.debug(f"Removing callback '{tag}' for setting '{self._name}'.")
            del self._callbacks[tag]

    def _update(self, value):
        if str(value).lower() != str(self._value).lower():
            try:
                encoded_value = self.validate(value)
            except Exception as e:
                status.error_message(f"Failed validating value {value} for setting '{self._name}':\n{e}")
                return

            if encoded_value is not None:
                _logger.debug(f"Changed setting '{self._name}' from '{self._value}' to '{encoded_value}'.")
                old_value = self._value
                self._value = encoded_value
                for k, v in self._callbacks.items():
                    _logger.debug(f"Calling callback {v} for setting {self._name}")
                    v(self._name, old_value, self._value)
            else:
                status.error_message(
                    f"Value '{value}' for setting '{self._name}' not supported. "
                    f"Allowed values are {self._validator.allowed_values_as_string}.")

    def _set_default(self):
        _logger.debug(f"Changing setting '{self._name}' to default value '{self._default}.")
        self._update(self._default)

class EnumSetting(SingleSetting):
    def __init__(self, name, allowed_values, value):
        super().__init__(name, value, EnumValidator(allowed_values))

class LogLevelSetting(EnumSetting):
    def __init__(self, name, value):
        super().__init__(name, ['debug','info','warning','error'], value)

    def encode(self, value):
        if value is None:
            return None
        return getattr(logging, value.upper())

class IntegerRangeSetting(SingleSetting):
    def __init__(self, name, value, minimum, maximum):
        super().__init__(name, value, IntegerRangeValidator(minimum, maximum))

class TypeSetting(SingleSetting):
    def __init__(self, name, value):
        super().__init__(name, value, TypeValidator(type(value)))

class BooleanSetting(SingleSetting):
    def __init__(self, name, value):
        super().__init__(name, value, BooleanValidator())
