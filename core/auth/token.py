"""This module provides JWT token tools."""

from datetime import datetime, timedelta, timezone

from jwt import decode, encode
from pydantic import BaseModel

from .enums import Roles


class TokenPayload(BaseModel):
    uid: str
    username: str
    first_name: str = ''
    last_name: str = ''
    role: Roles | None = None
    exp: datetime | None = None


def create_token(
    data: TokenPayload,
    secret: str,
    minutes: int = 15,
    algorithm: str | None = 'HS256',
) -> str:
    """Creates a JWT token from
    a dict containing an user data.

    Parameters
    ----------
    data : TokenPayload
        Token data.
    secret : str
        Secret to encode de token payload.
    minutes : int, optional
        Token life time in minutes, by default 15.
    algorithm : str, optional
        Encoding algorithm, by default 'HS256'.

    Returns
    -------
    str
        JWT token.
    """
    payload = {
        'uid': data.uid,
        'username': data.username,
        'first_name': data.first_name,
        'last_name': data.last_name,
        'role': data.role,
        'exp': data.exp
        or datetime.now(timezone.utc) + timedelta(minutes=minutes),
    }
    return encode(payload, secret, algorithm=algorithm)


def decode_token(
    token: str, secret: str, algorithm: str | None = 'HS256'
) -> TokenPayload:
    """Decodes a token.

    Parameters
    ----------
    token : str
        Access token.
    secret : str
        Secret to decode the token.
    algorithm : str, optional
        Encoding algorithm, by default 'HS256'.

    Returns
    -------
    TokenPayload
        Decoded token.
    """
    payload = decode(
        token, secret, algorithms=[algorithm] if algorithm else None
    )
    return TokenPayload(**payload)
