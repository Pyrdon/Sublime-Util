import logging
logger = logging.getLogger(__name__)

from . import log

def init(local_settings_module):
    """
    Called whenever the plugin is loaded

    :param local_settings_module: The plugin's settings module
    """

    logger.debug("Plugin loaded.")
    # Settings are initialized in the log module to ensure that the settings object exists, but to also be
    # able to log initialization
    log.init(local_settings_module)

def deinit(local_settings_module):
    """
    Called whenever the plugin is unloaded

    :param local_settings_module: The plugin's settings module
    """

    logger.debug("Plugin unloaded.")
    log.deinit(local_settings_module)
