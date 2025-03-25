"""This module provides the user session data class."""

from datetime import datetime, timezone
from uuid import UUID

from starlette.authentication import BaseUser

from .enums import Roles


class UserSession(BaseUser):
    """User session handler."""

    uid: UUID
    username: str
    first_name: str
    last_name: str
    role: Roles | None = None
    exp: datetime | None = None

    error_message: str | None
    """Authentication error message."""

    def __init__(
        self,
        uid: UUID,
        username: str,
        first_name: str = '',
        last_name: str = '',
        role: Roles | None = None,
        exp: datetime | None = None,
    ) -> None:
        self.uid = uid
        self.role = role
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.exp = exp
        self.error_message = None

    @property
    def is_authenticated(self) -> bool:
        """Checks if user is authenticated."""
        if not self.exp or self.exp < datetime.now(timezone.utc):
            return False

        return True if self.uid and self.username else False

    @property
    def display_name(self) -> str:
        """User's display name."""
        return f'{self.first_name} {self.last_name}'.strip()

    @property
    def identity(self) -> UUID:
        """User's ID."""
        return self.uid

    async def has_role(self, role: Roles) -> bool:
        """Checks if user has a role.

        Parameters
        ----------
        role : Roles
            Role to compare to the user's role.

        Returns
        -------
        bool
            Whether roles match.
        """
        if self.role == Roles.ADMIN:
            return True

        return self.role == role


class UnauthenticatedUserSession(UserSession):
    """Unauthenticated user session handler."""

    def __init__(self, error_message: str) -> None:
        self.uid = UUID('00000000-0000-0000-0000-000000000000')
        self.username = ''
        self.first_name = ''
        self.last_name = ''
        self.error_message = error_message

    @property
    def is_authenticated(self) -> bool:
        return False

    @property
    def display_name(self) -> str:
        return ''

    @property
    def identity(self) -> str:
        return ''

    async def has_role(self, _: Roles) -> bool:
        return False
