"""This module provides the ``main`` logger for the application
and the ``get_logger`` function to get a logger with a different name.

Import the logger as follows:
>>> from core import logger

And use it as follows:
>>> logger.debug('A quirky message only developers care about')
>>> logger.info('Curious users might want to know this')
>>> logger.warning('Something is wrong and any user should be informed')
>>> logger.error('Serious stuff, this is red for a reason')
>>> logger.critical('OH NO! everything is on fire')

Getting a logger with a different name:
>>> from core.logger import get_logger
>>> logger = get_logger('my_logger')

To configure the logger, set the ``LOGGER_CONF_FILE`` environment
variable to the path of the logger configuration file.

If the ``LOGGER_CONF_FILE`` environment variable is not set,
it defaults to ``logger.conf`` in the root directory.

If the logger configuration file is not found,
a ``FileNotFoundError`` is raised.
"""

from logging import Logger, getLogger

from .settings import Settings


def get_logger(name: str = 'main') -> Logger:
    """Returns a logger based on the configuration file
    set to the ``LOGGER_CONF_FILE`` environment variable.

    If the ``LOGGER_CONF_FILE`` environment variable is not set,
    it defaults to ``logger.conf`` in the root directory.

    Parameters
    ----------
    name : str, optional
        The name of the logger, by default 'main'.
    """

    logger = getLogger(name)
    if Settings.server.PROD:
        logger.setLevel(Settings.logger.PROD_LOG_LEVEL)
    else:
        logger.setLevel(Settings.logger.DEV_LOG_LEVEL)
    return logger


logger = get_logger()
"""The ``main`` logger for the application."""
