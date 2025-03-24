"""Posts management service."""

from abc import ABC, abstractmethod
from uuid import UUID

from odata_v4_query import ODataQueryOptions
from sqlactive.definitions import SUBQUERY
from sqlactive.types import EagerSchema

from core import I18N
from core.bases.base_service import BaseService
from dtos.post_dto import (
    PostCreateRequestDTO,
    PostResponseDTO,
    PostUpdateRequestDTO,
    PublisherResponseDTO,
    RelatedCommentResponseDTO,
    RelatedReactionResponseDTO,
)
from models.db import Post
from utils.pagination import PaginatedResponse


class IPostService(BaseService, ABC):
    """Posts management service interface."""

    @abstractmethod
    async def list_posts(
        self, odata_options: ODataQueryOptions
    ) -> PaginatedResponse[PostResponseDTO]:
        """List posts.

        Parameters
        ----------
        odata_options : ODataQueryOptions
            OData query options.

        Returns
        -------
        PaginatedResponse[PostResponseDTO]
            List of posts.
        """

    @abstractmethod
    async def get_post(self, uid: str) -> PostResponseDTO | None:
        """Gets a post with the provided ID.

        Parameters
        ----------
        uid : str
            Post ID.

        Returns
        -------
        PostResponseDTO | None
            Post if found.
        """

    @abstractmethod
    async def create_post(
        self, data: PostCreateRequestDTO, publisher: str
    ) -> PostResponseDTO:
        """Creates a new post.

        Parameters
        ----------
        data : PostCreateRequestDTO
            Data for the new post.
        publisher : str
            ID of the publisher.

        Returns
        -------
        PostResponseDTO
            Created post.
        """

    @abstractmethod
    async def update_post(
        self,
        uid: str,
        data: PostUpdateRequestDTO,
    ) -> PostResponseDTO | None:
        """Updates the post with the provided ID.

        Parameters
        ----------
        uid : str
            Post ID.
        data : PostUpdateRequestDTO
            New data for the post.

        Returns
        -------
        PostResponseDTO | None
            Updated post if found.
        """

    @abstractmethod
    async def delete_post(self, uid: str) -> None:
        """Deletes the post with the provided ID.

        Parameters
        ----------
        uid : str
            Post ID.
        """

    @abstractmethod
    def get_response_dto(self, post: Post) -> PostResponseDTO:
        """Gets the response DTO for the given post.

        Parameters
        ----------
        post : Post
            Post.

        Returns
        -------
        PostResponseDTO
            Response DTO.
        """


class PostService(IPostService):
    """Posts management service."""

    def __init__(self, t: I18N) -> None:
        self.t = t

    async def list_posts(
        self, odata_options: ODataQueryOptions
    ) -> PaginatedResponse[PostResponseDTO]:
        query = self.get_async_query(odata_options, Post)
        query.join(Post.publisher)

        if not odata_options.orderby:
            query.order_by('-created_at')

        posts = await query.unique_all()
        data = [self.get_response_dto(post) for post in posts]

        count = await self.get_odata_count(odata_options, query)
        return self.to_paginated_response(odata_options, data, count)

    async def get_post(self, uid: str) -> PostResponseDTO | None:
        post = await Post.get(UUID(uid), join=[Post.publisher])
        if post is None:
            return None

        return self.get_response_dto(post)

    async def create_post(
        self, data: PostCreateRequestDTO, publisher: str
    ) -> PostResponseDTO:
        post = await Post.create(
            title=data.title,
            body=data.body,
            tags=data.tags,
            publisher_id=UUID(publisher),
        )

        return self.get_response_dto(post)

    async def update_post(
        self,
        uid: str,
        data: PostUpdateRequestDTO,
    ) -> PostResponseDTO | None:
        post = await Post.get(UUID(uid))
        if post is None:
            return None

        post.title = data.title
        post.body = data.body
        post.tags = data.tags
        await post.save()

        return self.get_response_dto(post)

    async def delete_post(self, uid: str) -> None:
        post = await Post.get(UUID(uid))
        if post:
            await post.delete()

    def get_response_dto(self, post: Post) -> PostResponseDTO:
        comments = [
            RelatedCommentResponseDTO(uid=comment.uid, body=comment.body)
            for comment in post.comments
        ]

        reactions = [
            RelatedReactionResponseDTO(
                uid=reaction.uid,
                reactionType=reaction.reaction_type,
            )
            for reaction in post.reactions
        ]

        publisher = PublisherResponseDTO(
            username=post.publisher.username,
            firstName=post.publisher.first_name,
            lastName=post.publisher.last_name,
        )

        return PostResponseDTO(
            uid=post.uid,
            title=post.title,
            body=post.body,
            tags=post.tags,
            publisher=publisher,
            publishedAt=post.published_at,
            comments=comments,
            reactions=reactions,
            updatedAt=post.updated_at,
        )

    def get_expand_schema(self) -> EagerSchema:
        return {Post.comments: SUBQUERY, Post.reactions: SUBQUERY}
