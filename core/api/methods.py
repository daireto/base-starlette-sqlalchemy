"""This module provides the ``get``, ``post``, ``put``, ``patch`` and
``delete`` decorators to create the API endpoints.
"""

from asyncio import iscoroutinefunction
from collections.abc import Callable
from functools import wraps


def _get_wrapper(method: Callable, path: str, method_name: str):
    if not iscoroutinefunction(method):
        raise TypeError(f'endpoint method {method.__name__!r} must be async')

    @wraps(method)
    async def wrapper(self, *args, **kwargs):
        return await method(self, *args, **kwargs)

    setattr(wrapper, 'path', path)
    setattr(wrapper, 'method', method_name.upper())
    return wrapper


def get(path: str):
    """Creates a GET endpoint.

    Raises
    ------
    TypeError
        If the endpoint method is not async.

    Examples
    --------
    >>> class ExampleRouter(BaseRouter):
    ...     @get('/foo')
    ...     async def foo(self, *args, **kwargs):
    ...         pass
    """
    def decorator(method: Callable):
        return _get_wrapper(method, path, 'GET')

    return decorator


def post(path: str):
    """Creates a POST endpoint.

    Raises
    ------
    TypeError
        If the endpoint method is not async.

    Examples
    --------
    >>> class ExampleRouter(BaseRouter):
    ...     @post('/foo')
    ...     async def foo(self, data: RequestDTO, *args, **kwargs):
    ...         pass
    """
    def decorator(method: Callable):
        return _get_wrapper(method, path, 'POST')

    return decorator


def put(path: str):
    """Creates a PUT endpoint.

    Raises
    ------
    TypeError
        If the endpoint method is not async.

    Examples
    --------
    >>> class ExampleRouter(BaseRouter):
    ...     @put('/foo')
    ...     async def foo(self, id: str, data: RequestDTO, *args, **kwargs):
    ...         pass
    """
    def decorator(method: Callable):
        return _get_wrapper(method, path, 'PUT')

    return decorator


def patch(path: str):
    """Creates a PATCH endpoint.

    Raises
    ------
    TypeError
        If the endpoint method is not async.

    Examples
    --------
    >>> class ExampleRouter(BaseRouter):
    ...     @patch('/foo')
    ...     async def foo(self, id: str, data: RequestDTO, *args, **kwargs):
    ...         pass
    """
    def decorator(method: Callable):
        return _get_wrapper(method, path, 'PATCH')

    return decorator


def delete(path: str):
    """Creates a DELETE endpoint.

    Raises
    ------
    TypeError
        If the endpoint method is not async.

    Examples
    --------
    >>> class ExampleRouter(BaseRouter):
    ...     @delete('/foo')
    ...     async def foo(self, id: str, *args, **kwargs):
    ...         pass
    """
    def decorator(method: Callable):
        return _get_wrapper(method, path, 'DELETE')

    return decorator
