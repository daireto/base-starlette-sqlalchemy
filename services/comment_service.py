"""Comments management service."""

from abc import ABC, abstractmethod
from uuid import UUID

from odata_v4_query import ODataQueryOptions
from sqlactive.definitions import SUBQUERY
from sqlactive.types import EagerSchema

from core import I18N
from core.bases.base_service import BaseService
from dtos.comment_dto import (
    CommentAuthorResponseDTO,
    CommentCreateRequestDTO,
    CommentPostResponseDTO,
    CommentResponseDTO,
    CommentUpdateRequestDTO,
    RelatedReactionResponseDTO,
)
from models.db import Comment
from utils.pagination import PaginatedResponse


class ICommentService(BaseService, ABC):
    """Comments management service interface."""

    @abstractmethod
    async def list_comments(
        self, odata_options: ODataQueryOptions
    ) -> PaginatedResponse[CommentResponseDTO]:
        """List comments.

        Parameters
        ----------
        odata_options : ODataQueryOptions
            OData query options.

        Returns
        -------
        PaginatedResponse[CommentResponseDTO]
            List of comments.
        """

    @abstractmethod
    async def get_comment(self, uid: str) -> CommentResponseDTO | None:
        """Gets a comment with the provided ID.

        Parameters
        ----------
        uid : str
            Comment ID.

        Returns
        -------
        CommentResponseDTO | None
            Comment if found.
        """

    @abstractmethod
    async def create_comment(
        self, data: CommentCreateRequestDTO, publisher: str
    ) -> CommentResponseDTO:
        """Creates a new comment.

        Parameters
        ----------
        data : CommentCreateRequestDTO
            Data for the new comment.
        publisher : str
            ID of the publisher.

        Returns
        -------
        CommentResponseDTO
            Created comment.
        """

    @abstractmethod
    async def update_comment(
        self,
        uid: str,
        data: CommentUpdateRequestDTO,
    ) -> CommentResponseDTO | None:
        """Updates the comment with the provided ID.

        Parameters
        ----------
        uid : str
            Comment ID.
        data : CommentUpdateRequestDTO
            New data for the comment.

        Returns
        -------
        CommentResponseDTO | None
            Updated comment if found.
        """

    @abstractmethod
    async def delete_comment(self, uid: str) -> None:
        """Deletes the comment with the provided ID.

        Parameters
        ----------
        uid : str
            Comment ID.
        """

    @abstractmethod
    def get_response_dto(self, comment: Comment) -> CommentResponseDTO:
        """Gets the response DTO for the given comment.

        Parameters
        ----------
        comment : Comment
            Comment.

        Returns
        -------
        CommentResponseDTO
            Response DTO.
        """


class CommentService(ICommentService):
    """Comments management service."""

    def __init__(self, t: I18N) -> None:
        self.t = t

    async def list_comments(
        self, odata_options: ODataQueryOptions
    ) -> PaginatedResponse[CommentResponseDTO]:
        query = self.get_async_query(odata_options, Comment)
        query.join(Comment.user).join(Comment.post)

        if not odata_options.orderby:
            query.order_by('-created_at')

        comments = await query.unique_all()
        data = [self.get_response_dto(comment) for comment in comments]

        count = await self.get_odata_count(odata_options, query)
        return self.to_paginated_response(odata_options, data, count)

    async def get_comment(self, uid: str) -> CommentResponseDTO | None:
        comment = await Comment.get(
            UUID(uid), join=[Comment.user, Comment.post]
        )
        if comment is None:
            return None

        return self.get_response_dto(comment)

    async def create_comment(
        self, data: CommentCreateRequestDTO, publisher: str
    ) -> CommentResponseDTO:
        comment = await Comment.create(
            body=data.body,
            user_id=UUID(publisher),
            post_id=data.postId,
        )

        return self.get_response_dto(comment)

    async def update_comment(
        self,
        uid: str,
        data: CommentUpdateRequestDTO,
    ) -> CommentResponseDTO | None:
        comment = await Comment.get(UUID(uid))
        if comment is None:
            return None

        comment.body = data.body
        await comment.save()

        return self.get_response_dto(comment)

    async def delete_comment(self, uid: str) -> None:
        comment = await Comment.get(UUID(uid))
        if comment:
            await comment.delete()

    def get_response_dto(self, comment: Comment) -> CommentResponseDTO:
        reactions = [
            RelatedReactionResponseDTO(
                uid=reaction.uid,
                reactionType=reaction.reaction_type,
            )
            for reaction in comment.reactions
        ]

        author = CommentAuthorResponseDTO(
            username=comment.user.username,
            firstName=comment.user.first_name,
            lastName=comment.user.last_name,
        )

        post = CommentPostResponseDTO(
            uid=comment.post.uid, title=comment.post.title
        )

        return CommentResponseDTO(
            uid=comment.uid,
            body=comment.body,
            user=author,
            post=post,
            reactions=reactions,
            createdAt=comment.created_at,
            updatedAt=comment.updated_at,
        )

    def get_expand_schema(self) -> EagerSchema:
        return {Comment.reactions: SUBQUERY}
