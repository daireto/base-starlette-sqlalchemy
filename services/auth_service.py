"""Authentication service."""

from abc import ABC, abstractmethod

from passlib.hash import pbkdf2_sha256
from sqlalchemy import or_

from core import I18N
from core.api.errors import BadRequestError
from core.auth.enums import Roles
from core.auth.token import TokenPayload, create_token
from core.bases.base_service import BaseService
from core.settings import Settings
from dtos.auth_dto import LoginRequestDTO, SignupRequestDTO
from models.db import User


class IAuthService(BaseService, ABC):
    """Authentication service interface."""

    @abstractmethod
    async def login(self, data: LoginRequestDTO) -> str | None:
        """Logs in the user.

        Parameters
        ----------
        data : LoginRequestDTO
            Login data.

        Returns
        -------
        str | None
            Access token if authenticated.
        """

    @abstractmethod
    async def signup(self, data: SignupRequestDTO) -> str:
        """Creates a new user.

        Parameters
        ----------
        data : SignupRequestDTO
            Signup data.

        Returns
        -------
        str
            Access token.

        Raises
        ------
        BadRequestError
            If the user already exists.
        BadRequestError
            If the passwords don't match.
        """


class AuthService(BaseService):
    """Authentication service."""

    def __init__(self, t: I18N) -> None:
        self.t = t

    def __create_access_token(self, user: User) -> str:
        """Creates an access token
        for the provided user.

        Parameters
        ----------
        user : User
            User.

        Returns
        -------
        str
            Access token.
        """
        return create_token(
            data=TokenPayload(
                uid=user.uid,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role,
            ),
            secret=str(Settings.auth.ACCESS_TOKEN_SECRET),
            minutes=Settings.auth.ACCESS_TOKEN_EXPIRES_MINUTES,
            algorithm=Settings.auth.ACCESS_TOKEN_ENCODING_ALGORITHM,
        )

    async def login(self, data: LoginRequestDTO) -> str | None:
        user = await User.find(username=data.username).first()
        if user is None:
            return None

        if not user.verify_password(data.password):
            return None

        return self.__create_access_token(user)

    async def signup(self, data: SignupRequestDTO) -> str:
        if await User.find(
            or_(User.username == data.username, User.email == data.email)
        ).first():
            raise BadRequestError(self.t('user.user_already_exists'))

        if data.password is not None:
            if data.password != data.confirmPassword:
                raise BadRequestError(self.t('user.passwords_mismatch'))

        user = await User.create(
            username=data.username,
            password=pbkdf2_sha256.hash(data.password),
            first_name=data.firstName,
            last_name=data.lastName,
            email=data.email,
            role=Roles.USER,
            birthday=data.birthday,
            is_active=True,
        )

        return self.__create_access_token(user)
