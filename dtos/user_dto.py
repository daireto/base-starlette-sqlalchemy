from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator

from core.auth.enums import Roles
from core.bases.base_dto import BaseRequestDTO, BaseResponseDTO
from models.db import Gender


class SelfUserUpdateRequestDTO(BaseRequestDTO):
    username: str = Field(
        title='Username', description='Username', max_length=15
    )
    firstName: str = Field(
        title='First name', description='First name', max_length=50
    )
    lastName: str = Field(
        title='Last name', description='Last name', max_length=50
    )
    email: str = Field(title='Email', description='Email', max_length=70)
    gender: Gender = Field(title='Gender', description='Gender')
    birthday: datetime = Field(title='Birthday', description='Birthday')
    password: str | None = Field(
        title='Password',
        description='Only if you want to change the password.',
        min_length=8,
        max_length=24,
        default=None,
    )
    confirmPassword: str | None = Field(
        title='Password confirmation',
        description=(
            'Only if you want to change the password. '
            'It must be the same as the password.'
        ),
        default=None,
    )


class UserRequestDTO(BaseRequestDTO):
    username: str = Field(
        title='Username', description='Username', max_length=15
    )
    firstName: str = Field(
        title='First name', description='First name', max_length=50
    )
    lastName: str = Field(
        title='Last name', description='Last name', max_length=50
    )
    email: str = Field(title='Email', description='Email', max_length=70)
    gender: Gender = Field(title='Gender', description='Gender')
    birthday: datetime = Field(title='Birthday', description='Birthday')
    role: Roles = Field(title='Role', description='Role', default=Roles.USER)
    isActive: bool = Field(
        title='Is active',
        description='Indicates if the user is active.',
        default=True,
    )

    @field_validator('username')
    def username_lower(cls, v: str):
        return v.lower()

    @field_validator('email')
    def email_lower(cls, v: str):
        return v.lower()


class UserCreateRequestDTO(UserRequestDTO):
    password: str = Field(
        title='Password', description='Password', min_length=8, max_length=24
    )


class UserUpdateRequestDTO(UserRequestDTO):
    password: str | None = Field(
        title='Password',
        description='Only if you want to change the password.',
        min_length=8,
        max_length=24,
        default=None,
    )
    confirmPassword: str | None = Field(
        title='Password confirmation',
        description=(
            'Only if you want to change the password. '
            'It must be the same as the password.'
        ),
        default=None,
    )


class RelatedUserResponseDTO(BaseResponseDTO):
    uid: UUID = Field(title='UID', description='User ID')
    username: str = Field(title='Username', description='Username')
    firstName: str = Field(title='First name', description='First name')
    lastName: str = Field(title='Last name', description='Last name')
    role: Roles = Field(title='Role', description='Role')


class UserResponseDTO(BaseResponseDTO):
    uid: UUID = Field(title='UID', description='User ID')
    username: str = Field(title='Username', description='Username')
    firstName: str = Field(title='First name', description='First name')
    lastName: str = Field(title='Last name', description='Last name')
    email: str = Field(title='Email', description='Email')
    role: Roles = Field(title='Role', description='Role')
    gender: Gender = Field(title='Gender', description='Gender')
    birthday: datetime = Field(title='Birthday', description='Birthday')
    avatarURL: str = Field(
        title='Avatar URL',
        description='Unique avatar generated with Robohash.',
    )
    isActive: bool = Field(
        title='Is active',
        description='Indicates if the user is active',
        default=True,
    )
    createdAt: datetime = Field(
        title='Created at',
        description='Date when the user was created.',
    )
    updatedAt: datetime = Field(
        title='Updated at',
        description='Date when the user was last updated.',
    )
    createdBy: RelatedUserResponseDTO | None = Field(
        title='Created by',
        description='User who created the user.',
        default=None,
    )
    updatedBy: RelatedUserResponseDTO | None = Field(
        title='Updated by',
        description='Last user who updated the user.',
        default=None,
    )
