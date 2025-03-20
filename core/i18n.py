"""The ``I18N`` class to translate messages."""

from functools import reduce
from string import Template
from typing import Any

from .locales import locales
from .logger import logger
from .settings import Settings


class _TranslationTemplate(Template):
    delimiter = '{'


class I18N:
    """I18N translation class.

    Usage:
    >>> from core import I18N
    >>> t = I18N()

    Get the current locale:
    >>> t.locale
    'es'

    Translate a message:
    >>> t('foo')
    'bar'

    Translate a message with format values:
    >>> t('hello_to', name='Luis')
    'Hola Luis'

    Set or change the current locale:
    >>> t.locale = 'en_US'
    >>> t('hello_to', name='Luis')
    'Hello Luis'

    Note that if the locale is not found,
    the default locale ``es`` will be used.

    Get all the locales:
    >>> t.locales
    {'es': {'an_error_has_occurred': 'An error has occurred: {error}.', ...}, ...}
    """

    def __init__(self, locale: str | None = None) -> None:
        if locale is None:
            locale = Settings.locale.DEFAULT_LOCALE

        self.__locale = locale
        self.__locales = locales

    def __call__(self, key: str, **mapping: object) -> str:
        """Translate a message.

        Parameters
        ----------
        key : str
            Translation key.
        **mapping : object
            Mapping values.

        Returns
        -------
        str
            Translated message if found, otherwise, returns ``key``.
        """
        translations = self.__locales.get(self.__locale)
        if translations is None:
            logger.warning(f'Locale {self.__locale!r} not found')
            return key

        try:
            message = reduce(dict.__getitem__, key.split('.'), translations)
            if message is None:
                return key
        except KeyError:
            logger.warning(f'Translation key {key!r} not found')
            return key

        if not isinstance(message, str):
            logger.warning(f'Translation key {key!r} is not a string')
            return key

        return _TranslationTemplate(message).safe_substitute(mapping)

    @property
    def locale(self) -> str:
        """Current locale."""
        return self.__locale

    @locale.setter
    def locale(self, locale: str) -> None:
        """Set or change the current locale."""
        self.__locale = locale

    @property
    def locales(self) -> dict[str, dict[str, str | dict[str, Any]]]:
        """All the locales."""
        return self.__locales
