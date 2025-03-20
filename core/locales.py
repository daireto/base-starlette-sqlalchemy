"""This module provides the loaded locales."""

import glob
import os
from typing import Any

import orjson

from .definitions import ROOT_DIR
from .logger import logger
from .settings import Settings


def load_locales(
    locale_dir: str = 'locales',
) -> dict[str, dict[str, str | dict[str, Any]]]:
    """Load locales from the specified directory.

    Locale files must be ``json`` files named as follows:

        {locale_code}.json

    For example:

        en.json
        es.json
        fr.json
        de.json
        it.json

    Locale directory structure:

        .
        ├── locale_dir
            ├── en.json
            ├── es.json
            ├── fr.json
            ├── de.json
            ├── it.json
            └── ...

    This would return::

        {
            "en": {
                "hello": "Hello",
                "world": "World"
            },
            "es": {
                "hello": "Hola",
                "world": "Mundo"
            },
            "fr": {
                "hello": "Bonjour",
                "world": "Monde"
            },
            "de": {
                "hello": "Hallo",
                "world": "Welt"
            },
            "it": {
                "hello": "Ciao",
                "world": "Mondo"
            }
        }

    Parameters
    ----------
    locale_dir : str, optional
        The directory containing the locale files, by default 'locales'.

    Returns
    -------
    dict[str, dict[str, str | dict[str, Any]]]
        The loaded locales.
    """
    locales = {}

    LOCALE_DIR_PATH = os.path.join(ROOT_DIR, locale_dir)
    if not os.path.exists(LOCALE_DIR_PATH):
        logger.warning(f'Locale directory {locale_dir!r} does not exist')
        return locales

    logger.info(f'Searching locale files in {LOCALE_DIR_PATH!r}')
    for file in glob.glob(f'{LOCALE_DIR_PATH}/*'):
        if not os.path.isfile(file):
            continue

        if not file.endswith('.json'):
            continue

        try:
            filename = os.path.basename(
                file
            )  # Examples: en.json, es.json, ...
            with open(file, 'rb') as f:
                content = orjson.loads(f.read())
                locale_code = filename.rsplit('.', 1)[
                    0
                ]  # Remove extension (.json)
                locales[locale_code] = content
                logger.info(f'Loaded locale: {locale_code}')
        except Exception as e:
            logger.error(f'Locale file {file!r} could not be loaded: {e}')
            return locales

    if not locales:
        logger.warning('No locales found')

    return locales


locales = load_locales(Settings.locale.LOCALE_DIR)
"""The loaded locales."""
