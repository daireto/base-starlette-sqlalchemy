from uuid import uuid4

from starlette.requests import Request as StarletteRequest
from starlette.requests import empty_receive, empty_send
from starlette.types import Receive, Scope, Send
from starlette_di import ScopedServiceProvider
from starlette_di.definitions import SERVICE_PROVIDER_ARG_NAME

from core.auth.user import UserSession


class Request(StarletteRequest):
    """Handles the HTTP request."""

    id_: int
    user: UserSession
    service_provider: ScopedServiceProvider

    def __init__(
        self,
        scope: Scope,
        receive: Receive = empty_receive,
        send: Send = empty_send,
    ) -> None:
        super().__init__(scope, receive, send)
        self.id_ = int(uuid4())
        try:
            self.service_provider = scope[SERVICE_PROVIDER_ARG_NAME]
        except KeyError:
            raise RuntimeError(
                'No service provider found in request scope. '
                'Did you add the DependencyInjectionMiddleware?'
            )
