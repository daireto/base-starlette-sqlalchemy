"""This module contains utility functions."""

import logging
import os
import random
import string
import unicodedata
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlencode, urljoin, urlparse

from colorlog import ColoredFormatter


def get_robohash_url(username: str) -> str:
    """Gets the RoboHash URL.

    Parameters
    ----------
    username : str
        Username.

    Returns
    -------
    str
        RoboHash URL.
    """
    return f'https://robohash.org/{username}.png?size=500x500'


def check_file_exists(file_path: str) -> bool:
    """Checks if a file exists.

    Parameters
    ----------
    file_path : str
        File path.

    Returns
    -------
    bool
        True if the file exists, False otherwise.
    """
    return os.path.exists(file_path)


def generate_password(
    length: int = 16,
    digits: int = 4,
    uppercase_characters: int = 3,
    special_characters: int = 2,
) -> str:
    """Generates a random password.

    Parameters
    ----------
    length : int, optional
        Password length, by default 16.
    digits : int, optional
        Number of digits, by default 4.
    uppercase_characters : int, optional
        Number of uppercase characters, by default 3.
    special_characters : int, optional
        Number of special characters, by default 2.

    Returns
    -------
    str
        Generated password.
    """
    password = ''
    lowercase_characters = (
        length - digits - uppercase_characters - special_characters
    )
    for _ in range(uppercase_characters):
        password += random.choice(string.ascii_uppercase)
    for _ in range(lowercase_characters):
        password += random.choice(string.ascii_lowercase)
    for _ in range(digits):
        password += random.choice(string.digits)
    for _ in range(special_characters):
        password += random.choice('#$%&*.-')
    return password


def random_datetime(
    min_year: int = 1900,
    max_year: int = datetime.now().year,
    tz: timezone | None = None,
) -> datetime:
    """Generates a random datetime.

    Parameters
    ----------
    min_year : int, optional
        Minimum year, by default 1900.
    max_year : int, optional
        Maximum year, by default ``datetime.now().year``.
    tz : timezone, optional
        Timezone, by default None.

    Returns
    -------
    datetime
        Generated datetime.
    """
    start = datetime(min_year, 1, 1, 00, 00, 00, tzinfo=tz)
    years = max_year - min_year + 1
    end = start + timedelta(days=365 * years)
    return start + (end - start) * random.random()


def random_datetime_by_range(start: datetime, end: datetime) -> datetime:
    """Generates a random datetime by range.

    Parameters
    ----------
    start : datetime
        Start datetime.
    end : datetime
        End datetime.

    Returns
    -------
    datetime
        Generated datetime.
    """
    return start + (end - start) * random.random()


def get_colored_logger(
    name: str | None = None, level: int = logging.INFO
) -> logging.Logger:
    """Creates a logger using the
    ``colorlog.ColoredFormatter`` formatter.

    Parameters
    ----------
    name : str, optional
        Name of the logger, by default None.
    level : int, optional
        Level of the logger, by default logging.INFO.

    Returns
    -------
    logging.Logger
        Logger.
    """
    logger = logging.getLogger(name)
    formatter = ColoredFormatter(
        fmt=(
            '  %(log_color)s%(levelname)-8s%(reset)s | '
            '%(log_color)s%(asctime)s%(reset)s | '
            '%(log_color)s%(message)s%(reset)s'
        ),
        datefmt=r'%Y-%m-%d %H:%M:%S',
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger


def strip_accents(text: str) -> str:
    """Removes accents from a string.

    Parameters
    ----------
    text : str
        String to strip accents from.

    Returns
    -------
    str
        String without accents.
    """
    return ''.join(
        [
            c
            for c in unicodedata.normalize('NFKD', text)
            if not unicodedata.combining(c)
        ]
    )


def parse_accept_language(header_value: str) -> list[str]:
    """Parses the ``Accept-Language`` header value.

    ```python
    >>> parse_accept_language('en-ca,en;q=0.8,en-us;q=0.6,de-de;q=0.4,de;q=0.2')
    ['en', 'de']
    ```

    Parameters
    ----------
    header_value : str
        Accept-Language header value.

    Returns
    -------
    list[str]
        List of language codes.
    """
    languages = header_value.split(
        ','
    )  # Example: ['en-ca', 'en;q=0.8', de;q=0.2', ...]
    locale_codes = []
    for lang in languages:
        parts = lang.split(';', 1)  # Example: ('en', 'q=0.8')
        language_code = (
            parts[0].split('-', 1)[0].strip()
        )  # Example: 'en-ca' -> 'en'
        if language_code not in locale_codes:  # Avoid duplicates
            locale_codes.append(language_code)

    return locale_codes


def compute_odata_next_link(context: str, query: dict[str, list[str]]) -> str:
    """Computes the next link for an OData V4 response.

    Parameters
    ----------
    context : str
        Context of the request.
    query : dict[str, list[str]]
        Query parameters.

    Returns
    -------
    str
        Next link.
    """
    page = None
    if '$page' in query:
        page = int(query['$page'][0])
        query['$page'] = [str(page + 1)]

    if '$top' in query:
        top = int(query['$top'][0])
        if '$skip' in query:
            skip = int(query['$skip'][0]) + top
        elif page is not None:
            skip = page * top
        else:
            skip = top
        query['$skip'] = [str(skip)]

    return urljoin(context, '?' + urlencode(query, doseq=True))


def build_odata_response_body(
    request_url: str,
    data: list[dict[str, object]],
    count: int | None = None,
) -> dict[str, object]:
    """Builds an OData V4 JSON response.

    Parameters
    ----------
    request_url : str
        Request URL.
    data : list[dict[str, object]]
        Data to be returned.
    count : int, optional
        Total number of items, by default None.

    Returns
    -------
    dict[str, object]
        OData V4 JSON response.
    """
    context = request_url.rsplit('?', 1)[0]
    content: dict[str, object] = {'@odata.context': context}

    if count is not None:
        content['@odata.count'] = count

    content['value'] = data
    content['@odata.nextLink'] = compute_odata_next_link(
        context, parse_qs(urlparse(request_url).query)
    )

    return content
