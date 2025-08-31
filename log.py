import logging
import sublime

# Log level for informing for logging changes
EVENT_LEVEL = logging.INFO

# Global package logger
_pkg_name = __name__.split('.')[0]
_package_logger = logging.getLogger(_pkg_name)

# Local logger
_logger = logging.getLogger(__name__)

def init(default_log_level : str) -> None:
    """
    Initializes logging

    :param default_log_level: The default log level if not provided in settings file
    """

    # Set log formatter and add handler
    formatter = logging.Formatter(fmt="[{name}] {levelname}: {message}", style='{')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    _package_logger.addHandler(handler)

    # Special handling for log level setting to set it as early as possible
    sublime_settings = sublime.load_settings(f"{_pkg_name}.sublime-settings")
    # If the log level setting exists when package is enabled, just use the default and ignore it
    # It will be parsed again when saving the settings file and then this will issue an error
    # message
    try:
        log_level_name = sublime_settings.get('log_level', default_log_level).upper()
    except Exception as e:
        log_level_name = default_log_level.upper()
    log_level = getattr(logging, log_level_name)
    _package_logger.setLevel(log_level)

    # Prevent root logger from catching these logs
    _package_logger.propagate = False

    _logger.debug("Initialized logging.")

def deinit() -> None:
    """
    Deinitializes logging
    """

    for handler in _package_logger.handlers:
        _logger.debug(f"Removing log handler {handler}.")
        _package_logger.removeHandler(handler)

def on_log_lvl_change(name : str, old_val : str, new_val : str) -> None:
    """
    Called when the log level is changed

    :param name:    The name of the setting changed
    :param old_val: The old log level
    :param new_val: The new log level
    """

    return _on_log_lvl_change(name, old_val, new_val, _package_logger)

def init_local_logger(local_settings, logger : logging.Logger, setting_name : str) -> None:
    """
    Initializes a debug level of a local logger according to setting and handles its updates

    :param logger : The logger to modify the debug level of
    :setting_name : The name of the setting controlling it
    """

    def _on_local_log_lvl_change(name : str, old_val : str, new_val : str) -> None:
        return _on_log_lvl_change(name, old_val, new_val, logger)

    setting = getattr(local_settings, setting_name)

    # Set the log level
    log_level = getattr(logging, setting.value.upper())
    logger.setLevel(log_level)

    # Change on change of setting
    setting.add_on_change(setting_name, _on_local_log_lvl_change)

def deinit_local_logger(local_settings, setting_name : str) -> None:
    getattr(local_settings, setting_name).clear_on_change(setting_name)

def _on_log_lvl_change(name : str, old_val : str, new_val : str, logger : logging.Logger) -> None:
    """
    Internal-only function called when the log level is changed

    :param name:    The name of the setting changed
    :param old_val: The old log level
    :param new_val: The new log level
    :param logger:  The logger to update log level of
    """

    old_val = old_val.upper()
    new_val = new_val.upper()

    old_val_level = getattr(logging, old_val)
    new_val_level = getattr(logging, new_val)

    _settings_change_dbg_lvl = EVENT_LEVEL

    update_level = False
    if old_val_level > _settings_change_dbg_lvl:
        # The previous log level was too low for this settings change to have been logged
        if new_val_level > _settings_change_dbg_lvl:
            # and the updated log level is not high enough either
            # Temporarily increase the log level for this log entry
            logger.setLevel(_settings_change_dbg_lvl)
            update_level = True
        else:
            # New level is high enough, so set it directly
            logger.setLevel(new_val_level)
    else:
        # Old level was high enough - log first
        update_level = True

    _logger.log(_settings_change_dbg_lvl,
        f"Changing log level of logger '{logger.name}' from {old_val} to {new_val}.")

    if update_level:
        logger.setLevel(new_val_level)
