"""This module provides the ``BaseMiddleware`` class
to define middlewares.
"""

from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import Response


class BaseMiddleware(BaseHTTPMiddleware):
    """Base class for middlewares."""

    request: Request
    response: Response

    async def before_dispatch(self) -> None:
        """Task to run before dispatching the response."""
        pass

    async def after_dispatch(self) -> None:
        """Task to run after dispatching the response."""
        pass

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Dispatches the response.

        Calls the ``before_dispatch`` and ``after_dispatch`` tasks.

        Parameters
        ----------
        request : Request
            Request.
        call_next : RequestResponseEndpoint
            Endpoint response function.

        Returns
        -------
        Response
            Response.
        """
        self.request = request
        await self.before_dispatch()
        self.response = await call_next(self.request)
        await self.after_dispatch()
        return self.response
