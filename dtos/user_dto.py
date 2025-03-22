from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator

from core.auth.enums import Roles
from core.bases.base_dto import BaseRequestDTO, BaseResponseDTO
from models.db import Gender, Reactions


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
    username: str = Field(title='Username', description='Username')
    firstName: str = Field(title='First name', description='First name')
    lastName: str = Field(title='Last name', description='Last name')


class RelatedPostResponseDTO(BaseResponseDTO):
    uid: UUID = Field(title='UID', description='Post ID')
    title: str = Field(title='Title', description='Title')


class RelatedCommentResponseDTO(BaseResponseDTO):
    uid: UUID = Field(title='UID', description='Comment ID')
    body: str = Field(title='Body', description='Body')


class RelatedPostReactionResponseDTO(BaseResponseDTO):
    uid: UUID = Field(title='UID', description='Post reaction ID')
    reactionType: Reactions = Field(
        title='Reaction type', description='Reaction type'
    )
    post: RelatedPostResponseDTO = Field(
        title='Post', description='Post where the reaction was created.'
    )


class RelatedCommentReactionResponseDTO(BaseResponseDTO):
    uid: UUID = Field(title='UID', description='Comment reaction ID')
    reactionType: Reactions = Field(
        title='Reaction type', description='Reaction type'
    )
    comment: RelatedCommentResponseDTO = Field(
        title='Comment',
        description='Comment where the reaction was created.',
    )


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
    posts: list[RelatedPostResponseDTO] = Field(
        title='Posts', description='Posts created by the user.', default=[]
    )
    comments: list[RelatedCommentResponseDTO] = Field(
        title='Comments',
        description='Comments created by the user.',
        default=[],
    )
    post_reactions: list[RelatedPostReactionResponseDTO] = Field(
        title='Post reactions',
        description='Post reactions created by the user.',
        default=[],
    )
    comment_reactions: list[RelatedCommentReactionResponseDTO] = Field(
        title='Comment reactions',
        description='Comment reactions created by the user.',
        default=[],
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
    createdAt: datetime = Field(
        title='Created at',
        description='Date when the user was created.',
    )
    updatedAt: datetime = Field(
        title='Updated at',
        description='Date when the user was last updated.',
    )
