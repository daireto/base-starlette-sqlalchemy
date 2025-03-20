"""This module provides the ``Settings`` class
to get the configuration of the application.
"""

import os
from dataclasses import dataclass
from typing import Literal

from sqlactive import DBConnection
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret

from utils.func import check_file_exists

from .definitions import ROOT_DIR

config = Config('.env')
"""Configuration object.

Loads the environment variables in the following order:

1. Environment variables.
2. The ``.env`` file.
3. Default values.
"""


@dataclass
class ServerStatus:
    """Server status."""

    status: Literal['ok', 'error']
    """Server status.

    Default: ``ok``
    """

    message: str
    """Server status message.

    Default: ``Server is running.``
    """


@dataclass
class ServerConfig:
    """Server configuration."""

    HTTP_SCHEMA: str
    """Server schema.

    Default: ``http``
    """

    HOST: str
    """Host name.

    Default: ``localhost``
    """

    PROD: bool
    """Production mode flag.

    Default: ``False``
    """

    PORT: int
    """Port number.

    Default: ``8000``
    """


@dataclass
class APISpecConfig:
    """API spec configuration."""

    OPENAPI_TITLE: str
    """OpenAPI title.

    Default: ``API``
    """

    OPENAPI_DESCRIPTION: str
    """OpenAPI description.

    Default: ``API description``
    """

    OPENAPI_VERSION: str
    """OpenAPI version.

    Default: ``0.0.1``
    """


@dataclass
class TrustedHostConfig:
    """Trusted host configuration."""

    ALLOWED_HOSTS: list[str]
    """Allowed hosts for ``starlette.middleware.trustedhost.TrustedHostMiddleware``.

    Example: ``["localhost", "127.0.0.1", "0.0.0.0"]``

    Default: ``["*"]``
    """


@dataclass
class CorsConfig:
    """CORS configuration."""

    ALLOW_ORIGINS: list[str]
    """Allowed origins for ``starlette.middleware.cors.CORSMiddleware``.

    Example: ``["http://localhost", "http://127.0.0.1", "http://0.0.0.0"]``

    Default: ``["*"]``
    """

    ALLOW_METHODS: list[str]
    """Allowed methods for ``starlette.middleware.cors.CORSMiddleware``.

    Example: ``["GET", "POST", "PUT", "DELETE"]``

    Default: ``["*"]``
    """

    ALLOW_HEADERS: list[str]
    """Allowed headers for ``starlette.middleware.cors.CORSMiddleware``.

    Example: ``["Authorization", "Content-Type"]``

    Default: ``["*"]``
    """

    EXPOSE_HEADERS: list[str]
    """Exposed headers for ``starlette.middleware.cors.CORSMiddleware``.

    Example: ``["Authorization", "Content-Disposition"]``
    """


@dataclass
class LoggerConfig:
    """Logger configuration."""

    LOGGER_CONF_FILE: str
    """Path to the logger configuration file.

    Default: ``logger.conf``
    """

    DEV_LOG_LEVEL: str
    """Development log level.

    Default: ``DEBUG``
    """

    PROD_LOG_LEVEL: str
    """Production log level.

    Default: ``INFO``
    """


@dataclass
class LocaleConfig:
    """Locale configuration."""

    LOCALE_DIR: str
    """Locale directory.

    Default: ``locales``
    """

    DEFAULT_LOCALE: str
    """Default locale.

    Default: ``es``
    """


@dataclass
class AuthConfig:
    """Authentication configuration."""

    ACCESS_TOKEN_SECRET: str
    """Access token secret."""

    ACCESS_TOKEN_EXPIRES_MINUTES: int
    """Access token life time in minutes.

    Default: ``30``
    """

    ACCESS_TOKEN_ENCODING_ALGORITHM: str
    """Access token encoding algorithm.

    Default: ``HS256``
    """


@dataclass
class DatabaseConfig:
    """Database configuration."""

    DATABASE_URL: str
    """Database URL.

    Example: ``postgresql://postgres:postgres@localhost:5432/postgres``
    """

    FETCH_LIMIT: int = 100
    """Limit for fetching data from the database.

    Default: ``100``
    """


@dataclass
class AdminConfig:
    """Admin interface configuration."""

    SESSION_SECRET_KEY: str
    """Session secret key."""


class Settings:
    """Settings for the application."""

    status = ServerStatus(
        status='ok',
        message='Server is running',
    )
    """Server status."""

    server = ServerConfig(
        HTTP_SCHEMA=config('HTTP_SCHEMA', default='http'),
        HOST=config('HOST', default='localhost'),
        PROD=config('PROD', cast=bool, default=False),
        PORT=config('PORT', cast=int, default=8000),
    )
    """Server configuration."""

    api_spec = APISpecConfig(
        OPENAPI_TITLE=config('OPENAPI_TITLE', default='API'),
        OPENAPI_DESCRIPTION=config(
            'OPENAPI_DESCRIPTION', default='API description'
        ),
        OPENAPI_VERSION=config('OPENAPI_VERSION', default='0.0.1'),
    )
    """API spec configuration."""

    trusted_host = TrustedHostConfig(
        ALLOWED_HOSTS=list(
            config('ALLOWED_HOSTS', cast=CommaSeparatedStrings, default='*')
        ),
    )
    """Trusted host configuration."""

    cors = CorsConfig(
        ALLOW_ORIGINS=list(
            config('ALLOW_ORIGINS', cast=CommaSeparatedStrings, default='*')
        ),
        ALLOW_METHODS=list(
            config('ALLOW_METHODS', cast=CommaSeparatedStrings, default='*')
        ),
        ALLOW_HEADERS=list(
            config('ALLOW_HEADERS', cast=CommaSeparatedStrings, default='*')
        ),
        EXPOSE_HEADERS=list(
            config('EXPOSE_HEADERS', cast=CommaSeparatedStrings, default='')
        ),
    )
    """CORS configuration."""

    logger = LoggerConfig(
        LOGGER_CONF_FILE=config('LOGGER_CONF_FILE', default='logger.conf'),
        DEV_LOG_LEVEL=config('DEV_LOG_LEVEL', default='DEBUG'),
        PROD_LOG_LEVEL=config('PROD_LOG_LEVEL', default='INFO'),
    )
    """Logger configuration."""

    locale = LocaleConfig(
        LOCALE_DIR=config('LOCALE_DIR', default='locales'),
        DEFAULT_LOCALE=config('DEFAULT_LOCALE', default='es'),
    )
    """Locale configuration."""

    auth = AuthConfig(
        ACCESS_TOKEN_SECRET=str(
            config('ACCESS_TOKEN_SECRET', cast=Secret, default='')
        ),
        ACCESS_TOKEN_EXPIRES_MINUTES=config(
            'ACCESS_TOKEN_EXPIRES_MINUTES', cast=int, default=30
        ),
        ACCESS_TOKEN_ENCODING_ALGORITHM=config(
            'ACCESS_TOKEN_ENCODING_ALGORITHM', default='HS256'
        ),
    )
    """Authentication configuration."""

    database = DatabaseConfig(
        DATABASE_URL=str(config('DATABASE_URL', cast=Secret, default='')),
        FETCH_LIMIT=config('FETCH_LIMIT', cast=int, default=100),
    )
    """Database configuration."""

    admin = AdminConfig(
        SESSION_SECRET_KEY=str(
            config('SESSION_SECRET_KEY', cast=Secret, default='foo-bar-baz')
        ),
    )
    """Admin interface configuration."""

    @classmethod
    def get_logger_conf(cls) -> str:
        """Gets the logger configuration.

        Returns
        -------
        str
            Path to the logger configuration file.

        Raises
        ------
        FileNotFoundError
            If the logger configuration file is not found.
        """
        if check_file_exists(
            os.path.join(ROOT_DIR, cls.logger.LOGGER_CONF_FILE)
        ):
            return cls.logger.LOGGER_CONF_FILE

        raise FileNotFoundError(
            f'logger configuration file {cls.logger.LOGGER_CONF_FILE!r} '
            'not found'
        )

    @classmethod
    def create_db_connection(cls) -> DBConnection:
        """Creates a database connection.

        Returns
        -------
        DBConnection
            Database connection.

        Raises
        ------
        ValueError
            If ``DATABASE_URL`` is not set.
        """
        database_url = str(cls.database.DATABASE_URL)
        if not database_url:
            raise ValueError('environment variable DATABASE_URL is not set')
        return DBConnection(str(database_url), echo=False)

    @classmethod
    def get_server_url(cls) -> str:
        """Gets the server URL.

        Returns
        -------
        str
            Server URL.
        """
        return (
            f'{cls.server.HTTP_SCHEMA}://{cls.server.HOST}:{cls.server.PORT}'
        )
