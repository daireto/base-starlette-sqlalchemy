"""This module provides the ``auth`` endpoint decorator."""

from collections.abc import Callable
from functools import wraps
from inspect import isclass

from starlette.responses import JSONResponse, Response

from core import I18N
from core.bases.base_router import BaseRouter
from core.definitions import AUTH_REQUIRED

from .enums import Roles


def _auth_endpoint_decorator(endpoint: Callable, role: Roles | None = None):
    """Authentication endpoint decorator.

    Parameters
    ----------
    endpoint : Callable
        Endpoint function.
    role : Roles | None, optional
        Required role, by default None.
    """

    @wraps(endpoint)
    async def wrapper(self: BaseRouter, *args, **kwargs) -> Response:
        if not self.request.user.is_authenticated:
            return JSONResponse(
                {'message': self.request.user.error_message}, 401
            )

        if role and not await self.request.user.has_role(role):
            t = I18N(self.language)
            return JSONResponse({'message': t('auth.unauthorized')}, 403)

        return await endpoint(self, *args, **kwargs)

    setattr(wrapper, AUTH_REQUIRED, True)
    return wrapper


def auth(role: Roles | None = None):
    """Checks if the client is authenticated
    and checks its role if ``role`` is given.

    If client is not authenticated,
    returns an unauthorized error response (401).

    If the client's role does not match ``role`` if given,
    returns an forbidden error response (403).

    Usage:

    - Decorate an endpoint::

        from core.auth.decorator import auth

        class ExampleRouter(BaseRouter):

            @auth()
            @get('/foo')
            async def foo(self):
                return JSONResponse({'foo': 'bar'})

    - Decorate an endpoint with a role::

        from core.auth.enums import Roles

        class ExampleRouter(BaseRouter):

            @auth(Roles.ADMIN)
            @get('/foo')
            async def foo(self):
                return JSONResponse({'foo': 'bar'})

    - Decorate a router::

        @auth()
        class ExampleRouter(BaseRouter):

            @get('/foo')
            async def foo(self):
                return JSONResponse({'foo': 'bar'})

    - Decorate a router with a role::

        @auth(Roles.ADMIN)
        class ExampleRouter(BaseRouter):

            @get('/foo')
            async def foo(self):
                return JSONResponse({'foo': 'bar'})
    """

    def decorator(
        endpoint_or_router: Callable | type[BaseRouter],
    ) -> Callable | type[BaseRouter]:
        if isclass(endpoint_or_router):
            for name, fn in endpoint_or_router.__dict__.items():
                if getattr(fn, AUTH_REQUIRED, False):
                    continue

                if hasattr(fn, 'path') and hasattr(fn, 'method'):
                    setattr(
                        endpoint_or_router,
                        name,
                        _auth_endpoint_decorator(fn, role),
                    )

            return endpoint_or_router

        return _auth_endpoint_decorator(endpoint_or_router, role)

    return decorator
