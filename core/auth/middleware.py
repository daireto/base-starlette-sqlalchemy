"""This module provides the ``AuthenticationMiddlewareBackend``
class to authenticate requests.
"""

from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from pydantic import ValidationError
from starlette.authentication import AuthCredentials, AuthenticationBackend
from starlette.requests import HTTPConnection

from core import I18N
from core.settings import Settings
from utils.func import parse_accept_language

from .token import decode_token
from .user import UnauthenticatedUserSession, UserSession


class AuthenticationMiddlewareBackend(AuthenticationBackend):
    """Authentication middleware backend."""

    t: I18N

    def __init__(self, *args, **kwargs) -> None:
        self.t = I18N()
        super().__init__(*args, **kwargs)

    def __validate_access_token(
        self, conn: HTTPConnection
    ) -> tuple[AuthCredentials, UserSession] | None:
        """Validates the access token.

        Searches for the access token in the ``Authorization`` header.
        If not found, searches for the access token in
        the ``access_token`` cookie.

        Parameters
        ----------
        conn : HTTPConnection
            Connection instance.

        Returns
        -------
        tuple[AuthCredentials, UserSession] | None
            Tuple containing the authentication credentials
            and the user session if the token is valid.
        """
        token_data = None

        # Find the access token in the ``Authorization`` header
        authorization = conn.headers.get('Authorization')
        if authorization:
            schema_and_token = authorization.split()
            if len(schema_and_token) != 2:
                return (
                    AuthCredentials(),
                    UnauthenticatedUserSession(self.t('auth.unauthenticated')),
                )

            schema, token = schema_and_token
            if schema != 'Bearer':
                return (
                    AuthCredentials(),
                    UnauthenticatedUserSession(
                        self.t(
                            'auth.token_schema_not_supported', schema=schema
                        )
                    ),
                )

            token_data = decode_token(
                token=token,
                secret=str(Settings.auth.ACCESS_TOKEN_SECRET),
                algorithm=Settings.auth.ACCESS_TOKEN_ENCODING_ALGORITHM,
            )

        # Find the access token in the cookie
        cookie = conn.cookies.get('access_token')
        if cookie:
            token_data = decode_token(
                token=cookie,
                secret=str(Settings.auth.ACCESS_TOKEN_SECRET),
                algorithm=Settings.auth.ACCESS_TOKEN_ENCODING_ALGORITHM,
            )

        if not token_data:
            return (
                AuthCredentials(),
                UnauthenticatedUserSession(self.t('auth.unauthenticated')),
            )

        return (
            AuthCredentials(['authenticated']),
            UserSession(**token_data.model_dump()),
        )

    async def authenticate(
        self, conn: HTTPConnection
    ) -> tuple[AuthCredentials, UserSession] | None:
        """Authenticates the request.

        Authentication may fail due to the following reasons:
        - Token schema not supported.
        - Expired token.
        - Invalid token.
        - Could not decode token.

        Parameters
        ----------
        conn : HTTPConnection
            Connection instance.

        Returns
        -------
        tuple[AuthCredentials, UserSession] | None
            Tuple containing the authentication credentials
            and the user session.
        """
        accept_language = conn.headers.get('Accept-Language')
        if accept_language:
            self.t.locale = parse_accept_language(accept_language)[0]

        try:
            return self.__validate_access_token(conn)
        except ExpiredSignatureError:
            error_message = self.t('auth.expired_token')
        except (InvalidTokenError, ValidationError):
            error_message = self.t('auth.invalid_token')
        except Exception as e:
            error_message = self.t('auth.could_not_decode_token', error=str(e))

        return (AuthCredentials(), UnauthenticatedUserSession(error_message))
