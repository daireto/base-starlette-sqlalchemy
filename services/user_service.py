"""Users management service."""

from abc import ABC, abstractmethod
from uuid import UUID

from odata_v4_query import ODataQueryOptions
from passlib.hash import pbkdf2_sha256
from sqlactive.definitions import JOINED, SUBQUERY
from sqlactive.types import EagerSchema
from sqlalchemy import or_

from core import I18N
from core.api.errors import BadRequestError
from core.bases.base_service import BaseService
from dtos.user_dto import (
    RelatedCommentReactionResponseDTO,
    RelatedCommentResponseDTO,
    RelatedPostReactionResponseDTO,
    RelatedPostResponseDTO,
    RelatedUserResponseDTO,
    SelfUserUpdateRequestDTO,
    UserCreateRequestDTO,
    UserResponseDTO,
    UserUpdateRequestDTO,
)
from models.db import CommentReaction, PostReaction, User
from utils.func import get_robohash_url
from utils.pagination import PaginatedResponse


class IUserService(BaseService, ABC):
    """Users management service interface."""

    @abstractmethod
    async def list_users(
        self, odata_options: ODataQueryOptions
    ) -> PaginatedResponse[UserResponseDTO]:
        """List users.

        Parameters
        ----------
        odata_options : ODataQueryOptions
            OData query options.

        Returns
        -------
        PaginatedResponse[UserResponseDTO]
            List of users.
        """

    @abstractmethod
    async def get_user(self, uid: str) -> UserResponseDTO | None:
        """Gets a user with the provided ID.

        Parameters
        ----------
        uid : str
            User ID.

        Returns
        -------
        UserResponseDTO | None
            User if found.
        """

    @abstractmethod
    async def create_user(
        self, data: UserCreateRequestDTO, creator_id: str
    ) -> UserResponseDTO:
        """Creates a new user.

        Parameters
        ----------
        data : UserCreateRequestDTO
            Data for the new user.
        creator_id : str
            ID of the creator.

        Returns
        -------
        UserResponseDTO
            Created user.

        Raises
        ------
        BadRequestError
            If the user already exists.
        """

    @abstractmethod
    async def update_user(
        self,
        uid: str,
        data: UserUpdateRequestDTO | SelfUserUpdateRequestDTO,
        updater_id: str,
    ) -> UserResponseDTO | None:
        """Updates the user with the provided ID.

        Parameters
        ----------
        uid : str
            User ID.
        data : UserUpdateRequestDTO | SelfUserUpdateRequestDTO
            New data for the user.
        updater_id : str
            ID of the updater.

        Returns
        -------
        UserResponseDTO | None
            Updated user if found.

        Raises
        ------
        BadRequestError
            If the user already exists.
        BadRequestError
            If the passwords don't match.
        """

    @abstractmethod
    async def delete_user(self, uid: str) -> None:
        """Deletes the user with the provided ID.

        Parameters
        ----------
        uid : str
            User ID.
        """

    @abstractmethod
    def get_response_dto(self, user: User) -> UserResponseDTO:
        """Gets the response DTO for the given user.

        Parameters
        ----------
        user : User
            User.

        Returns
        -------
        UserResponseDTO
            Response DTO.
        """


class UserService(IUserService):
    """Users management service."""

    def __init__(self, t: I18N) -> None:
        self.t = t

    async def list_users(
        self, odata_options: ODataQueryOptions
    ) -> PaginatedResponse[UserResponseDTO]:
        query = self.get_async_query(odata_options, User)
        query.join(User.created_by).join(User.updated_by)

        if not odata_options.orderby:
            query.order_by('username', '-created_at')

        users = await query.unique_all()
        data = [self.get_response_dto(user) for user in users]

        count = await self.get_odata_count(odata_options, query)
        return self.to_paginated_response(odata_options, data, count)

    async def get_user(self, uid: str) -> UserResponseDTO | None:
        user = await User.get(
            UUID(uid), join=[User.created_by, User.updated_by]
        )
        if user is None:
            return None

        return self.get_response_dto(user)

    async def create_user(
        self, data: UserCreateRequestDTO, creator_id: str
    ) -> UserResponseDTO:
        if await User.find(
            or_(User.username == data.username, User.email == data.email)
        ).first():
            raise BadRequestError(self.t('user.user_already_exists'))

        user = await User.create(
            username=data.username,
            password=pbkdf2_sha256.hash(data.password),
            first_name=data.firstName,
            last_name=data.lastName,
            email=data.email,
            role=data.role,
            birthday=data.birthday,
            is_active=data.isActive,
            created_by_id=UUID(creator_id),
            updated_by_id=UUID(creator_id),
        )

        return self.get_response_dto(user)

    async def update_user(
        self,
        uid: str,
        data: UserUpdateRequestDTO | SelfUserUpdateRequestDTO,
        updater_id: str,
    ) -> UserResponseDTO | None:
        user = await User.get(UUID(uid))
        if user is None:
            return None

        if (
            data.username != user.username
            and await User.find(User.username == data.username).first()
        ):
            raise BadRequestError(self.t('user.user_already_exists'))

        if (
            data.email != user.email
            and await User.find(User.email == data.email).first()
        ):
            raise BadRequestError(self.t('user.user_already_exists'))

        if data.password is not None:
            if data.password != data.confirmPassword:
                raise BadRequestError(self.t('user.passwords_mismatch'))

            user.set_password(data.password)

        user.username = data.username
        user.first_name = data.firstName
        user.last_name = data.lastName
        user.email = data.email
        user.gender = data.gender
        user.birthday = data.birthday
        user.updated_by_id = UUID(updater_id)
        if isinstance(data, UserUpdateRequestDTO):
            user.role = data.role
            user.is_active = data.isActive
        await user.save()

        return self.get_response_dto(user)

    async def delete_user(self, uid: str) -> None:
        user = await User.get(UUID(uid))
        if user:
            await user.delete()

    def get_response_dto(self, user: User) -> UserResponseDTO:
        posts = [
            RelatedPostResponseDTO(uid=post.uid, title=post.title)
            for post in user.posts
        ]

        comments = [
            RelatedCommentResponseDTO(uid=comment.uid, body=comment.body)
            for comment in user.comments
        ]

        post_reactions = [
            RelatedPostReactionResponseDTO(
                uid=reaction.uid,
                reactionType=reaction.reaction_type,
                post=RelatedPostResponseDTO(
                    uid=reaction.post.uid, title=reaction.post.title
                ),
            )
            for reaction in user.post_reactions
        ]

        comment_reactions = [
            RelatedCommentReactionResponseDTO(
                uid=reaction.uid,
                reactionType=reaction.reaction_type,
                comment=RelatedCommentResponseDTO(
                    uid=reaction.comment.uid, body=reaction.comment.body
                ),
            )
            for reaction in user.comment_reactions
        ]

        created_by = (
            RelatedUserResponseDTO(
                username=user.created_by.username,
                firstName=user.created_by.first_name,
                lastName=user.created_by.last_name,
            )
            if user.created_by
            else None
        )

        updated_by = (
            RelatedUserResponseDTO(
                username=user.updated_by.username,
                firstName=user.updated_by.first_name,
                lastName=user.updated_by.last_name,
            )
            if user.updated_by
            else None
        )

        return UserResponseDTO(
            uid=user.uid,
            username=user.username,
            firstName=user.first_name,
            lastName=user.last_name,
            email=user.email,
            role=user.role,
            gender=user.gender,
            birthday=user.birthday,
            avatarURL=get_robohash_url(user.username),
            isActive=user.is_active,
            posts=posts,
            comments=comments,
            postReactions=post_reactions,
            commentReactions=comment_reactions,
            createdBy=created_by,
            updatedBy=updated_by,
            createdAt=user.created_at,
            updatedAt=user.updated_at,
        )

    def get_expand_schema(self) -> EagerSchema:
        return {
            User.posts: SUBQUERY,
            User.comments: SUBQUERY,
            User.post_reactions: (
                SUBQUERY,
                {
                    PostReaction.post: JOINED,
                },
            ),
            User.comment_reactions: (
                SUBQUERY,
                {
                    CommentReaction.comment: JOINED,
                },
            ),
        }
