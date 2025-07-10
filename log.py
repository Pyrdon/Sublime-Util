import logging
import sublime

# Log level for informing for logging changes
EVENT_LEVEL = logging.INFO

# Global package logger
pkg_name = __name__.split('.')[0]
package_logger = logging.getLogger(pkg_name)

# Local logger
logger = logging.getLogger(__name__)

def init(default_log_level : str) -> None:
    """
    Initializes logging

    :param default_log_level: The default log level if not provided in settings file
    """

    # Set log formatter and add handler
    formatter = logging.Formatter(fmt="[{name}] {levelname}: {message}", style='{')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    package_logger.addHandler(handler)

    # Special handling for log level setting to set it as early as possible
    sublime_settings = sublime.load_settings(f"{pkg_name}.sublime-settings")
    # If the log level setting exists when package is enabled, just use the default and ignore it
    # It will be parsed again when saving the settings file and then this will issue an error
    # message
    try:
        log_level_name = sublime_settings.get('log_level', default_log_level).upper()
    except Exception as e:
        log_level_name = default_log_level.upper()
    log_level = getattr(logging, log_level_name)
    package_logger.setLevel(log_level)

    # Prevent root logger from catching these logs
    package_logger.propagate = False

    logger.debug("Initialized logging.")

def deinit() -> None:
    """
    Deinitializes logging
    """

    for handler in package_logger.handlers:
        logger.debug(f"Removing log handler {handler}.")
        package_logger.removeHandler(handler)

def _on_log_lvl_change(name : str, old_val : str, new_val : str) -> None:
    """
    Called when the log level is changed

    :param name:    The name of the setting changed
    :param old_val: The old log level
    :param new_val: The new log level
    """

    old_val_level = getattr(logging, old_val.upper())
    new_val_level = getattr(logging, new_val.upper())

    _settings_change_dbg_lvl = EVENT_LEVEL

    update_level = False
    if old_val_level > _settings_change_dbg_lvl:
        # The previous log level was too low for this settings change to have been logged
        if new_val_level > _settings_change_dbg_lvl:
            # and the updated log level is not high enough either
            # Temporarily increase the log level for this log entry
            package_logger.setLevel(_settings_change_dbg_lvl)
            update_level = True
        else:
            # New level is high enough, so set it directly
            package_logger.setLevel(new_val_level)
    else:
        # Old level was high enough - log first
        update_level = True

    logger.log(_settings_change_dbg_lvl,
        f"Changing log level from {old_val} to {new_val}.")

    if update_level:
        package_logger.setLevel(new_val_level)
