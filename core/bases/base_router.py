"""This module provides the ``BaseRouter`` class
to define routers.
"""

from abc import ABC

from odata_v4_query import ODataQueryOptions, ODataQueryParser
from starlette.templating import Jinja2Templates

from core import I18N, logger
from core.api.errors import (
    BadRequestError,
    ForbiddenError,
    HTTPError,
    NotFoundError,
    UnauthorizedError,
)
from core.api.request import Request
from core.api.responses import ErrorResponse
from core.settings import Settings
from utils.func import parse_accept_language


class BaseRouter(ABC):
    """Base class for routers."""

    request: Request
    """Request handler."""

    templates: Jinja2Templates
    """Templates handler."""

    base_path: str = ''
    """Base path for the router endpoints."""

    parser: ODataQueryParser
    """OData V4 query parser."""

    def __init__(
        self, request: Request, templates: Jinja2Templates, base_path: str = ''
    ) -> None:
        """Creates a new instance of the router class.

        Parameters
        ----------
        request : Request
            Request handler.
        templates : Jinja2Templates
            Templates handler.
        base_path : str, optional
            Base path for the router endpoints, by default ''.
        """
        self.request = request
        self.templates = templates
        self.base_path = base_path
        self.parser = ODataQueryParser()

    def prev(self) -> None:
        """Pre-configuration function.
        Called before executing the endpoints.
        """
        self.__set_i18n_locale_from_accept_language_header()

    @property
    def language(self) -> str | None:
        """Current language stored in the
        request state."""
        if not hasattr(self.request.state, 'language'):
            return None
        return self.request.state.language

    def parse_odata(self) -> ODataQueryOptions:
        """Parses the OData V4 query from the request URL.

        Returns
        -------
        ODataQueryOptions
            Parsed OData V4 query.
        """
        options = self.parser.parse_url(str(self.request.url))
        if options.top is None or options.top > Settings.database.FETCH_LIMIT:
            options.top = Settings.database.FETCH_LIMIT

        return options

    def error(self, message: str, status_code: int = 500) -> ErrorResponse:
        """Returns a HTTP error response.

        Parameters
        ----------
        message : str
            Error message.
        status_code : int, optional
            Error status code, by default 500.

        Returns
        ------
        ErrorResponse
            HTTP error response.
        """
        return ErrorResponse(HTTPError(message, status_code))

    def bad_request(self, message: str = 'Bad request') -> ErrorResponse:
        """Returns a HTTP 400 Bad request error.

        Parameters
        ----------
        message : str | None, optional
            Error message, by default 'Bad request'.

        Returns
        ------
        ErrorResponse
            Bad request error.
        """
        return ErrorResponse(BadRequestError(message))

    def not_found(self, message: str = 'Not found') -> ErrorResponse:
        """Returns a HTTP 404 Not found error.

        Parameters
        ----------
        message : str | None, optional
            Error message, by default 'Not found'.

        Returns
        ------
        ErrorResponse
            Not found error.
        """
        return ErrorResponse(NotFoundError(message))

    def unauthorized(self, message: str = 'Unauthorized') -> ErrorResponse:
        """Returns a HTTP 401 Unauthorized error.

        Parameters
        ----------
        message : str | None, optional
            Error message, by default 'Unauthorized'.

        Returns
        ------
        ErrorResponse
            Unauthorized error.
        """
        return ErrorResponse(UnauthorizedError(message))

    def forbidden(self, message: str = 'Forbidden') -> ErrorResponse:
        """Returns a HTTP 403 Forbidden error.

        Parameters
        ----------
        message : str | None, optional
            Error message, by default 'Forbidden'.

        Returns
        ------
        ErrorResponse
            Forbidden error.
        """
        return ErrorResponse(ForbiddenError(message))

    def __set_i18n_locale_from_accept_language_header(self) -> None:
        """Sets the locale for the request."""
        try:
            i18n = self.request.service_provider.get_service(I18N)
            accept_language = self.request.headers.get('Accept-Language')
            if accept_language is not None:
                i18n.locale = parse_accept_language(accept_language)[0]
        except KeyError as e:
            logger.warning(e)
        except Exception as e:
            logger.error(f'Could not set locale to I18N: {e}')

    def __get_int_query_param(self, name: str, default: int) -> int:
        try:
            value = self.request.query_params.get(name, default)
            return int(value)
        except ValueError:
            return default
