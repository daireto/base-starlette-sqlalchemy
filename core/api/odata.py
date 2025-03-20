from collections.abc import Callable

from core.definitions import USE_ODATA


def use_odata(endpoint: Callable) -> Callable:
    """Marks an endpoint as using OData V4 query.

    This decorator is used to indicate that the endpoint
    uses OData V4 query. This will be used to generate
    the OpenAPI documentation for the OData V4 query parameters.

    Parameters
    ----------
    endpoint : Callable
        Endpoint function.
    """
    async def wrapper(self, *args, **kwargs):
        return endpoint(self, *args, **kwargs)

    setattr(wrapper, USE_ODATA, True)
    return wrapper
