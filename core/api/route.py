"""This module provides the ``Route`` class
to create the API routes.
"""

from collections.abc import Callable
from functools import partial
from inspect import isfunction, ismethod

from pydantic import ValidationError
from starlette.routing import Route as StarletteRoute
from starlette.routing import compile_path, get_name
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette_di import inject_method

from core import logger
from core.bases.base_router import BaseRouter
from core.definitions import AUTH_REQUIRED, USE_ODATA
from core.errors import InvalidRoutePathError

from .errors import HTTPError
from .request import Request
from .responses import ErrorResponse


class Route(StarletteRoute):
    """API route."""

    def __init__(
        self,
        path: str,
        cls: type[BaseRouter],
        endpoint: Callable,
        *,
        methods: list[str] | None = None,
        name: str | None = None,
        include_in_schema: bool = True,
    ) -> None:
        """Creates an API route.

        Parameters
        ----------
        path : str
            Endpoint route.
        cls : type
            Endpoint class.
        endpoint : Callable
            Endpoint function.
        methods : list[str] | None, optional
            HTTP methods, by default None.
        name : str | None, optional
            Route name, by default None.
        include_in_schema : bool, optional
            Include in schema, by default True.

        Raises
        ------
        InvalidRoutePathError
            If the path is invalid.
        """
        if cls.base_path and not cls.base_path.startswith('/'):
            raise InvalidRoutePathError(
                f'invalid path {cls.base_path!r} on {cls.__name__}'
            )

        if not path.startswith('/'):
            raise InvalidRoutePathError(
                f'invalid path {path!r} on {cls.__name__}.{endpoint.__name__}'
            )

        path = self.__remove_trailing_slash(
            cls.base_path
        ) + self.__remove_trailing_slash(path)
        self.path = path
        self.endpoint = endpoint
        self.name = get_name(endpoint) if name is None else name
        self.include_in_schema = include_in_schema

        endpoint_handler = endpoint
        while isinstance(endpoint_handler, partial):
            endpoint_handler = endpoint_handler.func

        if isfunction(endpoint_handler) or ismethod(endpoint_handler):
            # endpoint is function or method.
            # treat it as ``func(request) -> response``
            self.app = self.__create_app(cls, endpoint)
            if methods is None:
                methods = ['GET']
        else:
            # endpoint is a class, treat it as ASGI app
            self.app = endpoint

        if methods is None:
            self.methods = None
        else:
            self.methods = {method.upper() for method in methods}
            if 'GET' in self.methods:
                self.methods.add('HEAD')

        self.path_regex, self.path_format, self.param_convertors = (
            compile_path(path)
        )

        path_security = (
            'protected'
            if getattr(endpoint, AUTH_REQUIRED, False)
            else 'public'
        )
        logger.debug(
            f'Created {path_security} route {path!r} for '
            f'{endpoint.__qualname__} with '
            f'methods {self.methods}'
        )

        if getattr(endpoint, USE_ODATA, False):
            logger.debug(
                f'Route {path!r} ({endpoint.__qualname__}) uses OData V4 query'
            )

    def __remove_trailing_slash(self, path: str) -> str:
        """Removes trailing ``/`` from ``path``."""
        return path[:-1] if path.endswith('/') else path

    def __create_app(
        self, router_class: type[BaseRouter], func: Callable
    ) -> ASGIApp:
        """Creates an ASGI app.

        Parameters
        ----------
        router_class : type[BaseRouter]
            Router class.
        func : Callable
            Endpoint function.

        Returns
        -------
        ASGIApp
            ASGI app.
        """

        async def app(scope: Scope, receive: Receive, send: Send) -> None:
            request = Request(scope, receive, send)
            router = router_class(request)

            try:
                router.prev()
                injected_func = partial(
                    inject_method(pass_request=False)(func), router, request
                )
                response = await injected_func()

            except ValidationError as e:
                response = ErrorResponse(e, status_code=400)

            except HTTPError as e:
                response = ErrorResponse(e)

            except Exception as e:
                logger.error(f'{func.__qualname__}: {e}')
                response = ErrorResponse(
                    'An unexpected error occurred. Please try again.'
                )

            await response(scope, receive, send)

        return app

    @staticmethod
    def get_from_routers(routers: list[type[BaseRouter]]) -> list['Route']:
        """Get routes from routers.

        Parameters
        ----------
        routers : list[type[BaseRouter]]
            List of routers.

        Returns
        -------
        list[Route]
            List of routes.
        """
        logger.debug('Loading routes from routers...')
        routes = []
        for router in routers:
            for _, endpoint in router.__dict__.items():
                if hasattr(endpoint, 'path') and hasattr(endpoint, 'method'):
                    routes.append(
                        Route(
                            endpoint.path,
                            router,
                            endpoint,
                            methods=[endpoint.method],
                        )
                    )

        return routes
