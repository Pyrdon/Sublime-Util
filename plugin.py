import logging
_logger = logging.getLogger(__name__)

from . import log

def init(local_settings_module, *, default_log_level = 'warning'):
    """
    Called whenever the plugin is loaded

    :param local_settings_module: The plugin's settings module
    :param default_log_level: The default log level if not provided in settings file
    """

    _logger.debug("Plugin loaded.")
    log.init(default_log_level)
    local_settings_module.settings.init(default_log_level, log._on_log_lvl_change)

def deinit(local_settings_module):
    """
    Called whenever the plugin is unloaded

    :param local_settings_module: The plugin's settings module
    """

    _logger.debug("Plugin unloaded.")
    local_settings_module.settings.deinit()
    log.deinit()
