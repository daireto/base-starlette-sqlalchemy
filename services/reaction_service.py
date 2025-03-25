"""Reactions management service."""

from abc import ABC, abstractmethod
from uuid import UUID

from odata_v4_query import ODataQueryOptions

from core import I18N
from core.bases.base_service import BaseService
from dtos.reaction_dto import (
    ReactionAuthorResponseDTO,
    ReactionCreateRequestDTO,
    ReactionResponseDTO,
    ReactionTargetType,
    TargetResponseDTO,
)
from models.db import CommentReaction, PostReaction
from utils.pagination import PaginatedResponse

Reaction = CommentReaction | PostReaction


class IReactionService(BaseService, ABC):
    """Reactions management service interface."""

    @abstractmethod
    async def list_reactions(
        self, odata_options: ODataQueryOptions, target_type: ReactionTargetType
    ) -> PaginatedResponse[ReactionResponseDTO]:
        """List reactions.

        Parameters
        ----------
        odata_options : ODataQueryOptions
            OData query options.
        target_type : ReactionTargetType
            Type of the target.

        Returns
        -------
        PaginatedResponse[ReactionResponseDTO]
            List of reactions.
        """

    @abstractmethod
    async def get_reaction(
        self, uid: UUID, target_type: ReactionTargetType
    ) -> ReactionResponseDTO | None:
        """Gets a reaction with the provided ID.

        Parameters
        ----------
        uid : UUID
            Reaction ID.
        target_type : ReactionTargetType
            Type of the target.

        Returns
        -------
        ReactionResponseDTO | None
            Reaction if found.
        """

    @abstractmethod
    async def create_reaction(
        self, data: ReactionCreateRequestDTO, publisher: UUID
    ) -> ReactionResponseDTO:
        """Creates a new reaction.

        Parameters
        ----------
        data : ReactionCreateRequestDTO
            Data for the new reaction.
        publisher : UUID
            ID of the publisher.

        Returns
        -------
        ReactionResponseDTO
            Created reaction.
        """

    @abstractmethod
    async def delete_reaction(
        self, uid: UUID, target_type: ReactionTargetType
    ) -> None:
        """Deletes the reaction with the provided ID.

        Parameters
        ----------
        uid : UUID
            Reaction ID.
        target_type : ReactionTargetType
            Type of the target.
        """

    @abstractmethod
    def get_response_dto(self, reaction: Reaction) -> ReactionResponseDTO:
        """Gets the response DTO for the given reaction.

        Parameters
        ----------
        reaction : Reaction
            Reaction.

        Returns
        -------
        ReactionResponseDTO
            Response DTO.
        """


class ReactionService(IReactionService):
    """Reactions management service."""

    def __init__(self, t: I18N) -> None:
        self.t = t

    async def list_reactions(
        self, odata_options: ODataQueryOptions, target_type: ReactionTargetType
    ) -> PaginatedResponse[ReactionResponseDTO]:
        if target_type == 'comment':
            query = self.get_async_query(odata_options, CommentReaction)
            query.join(CommentReaction.user).join(CommentReaction.comment)
        else:
            query = self.get_async_query(odata_options, PostReaction)
            query.join(PostReaction.user).join(PostReaction.post)

        if not odata_options.orderby:
            query.order_by('-created_at')

        reactions = await query.unique_all()
        data = [self.get_response_dto(reaction) for reaction in reactions]

        count = await self.get_odata_count(odata_options, query)  # type: ignore
        return self.to_paginated_response(odata_options, data, count)

    async def get_reaction(
        self, uid: UUID, target_type: ReactionTargetType
    ) -> ReactionResponseDTO | None:
        if target_type == 'comment':
            reaction = await CommentReaction.get(
                uid, join=[CommentReaction.user, CommentReaction.comment]
            )
        else:
            reaction = await PostReaction.get(
                uid, join=[PostReaction.user, PostReaction.post]
            )

        if reaction is None:
            return None

        return self.get_response_dto(reaction)

    async def create_reaction(
        self, data: ReactionCreateRequestDTO, publisher: UUID
    ) -> ReactionResponseDTO:
        if data.targetType == 'comment':
            reaction = await CommentReaction.create(
                reaction_type=data.reactionType,
                user_id=publisher,
                comment_id=data.targetId,
            )
            reaction = await CommentReaction.get_or_fail(
                reaction.uid, join=[CommentReaction.user, CommentReaction.comment]
            )
        else:
            reaction = await PostReaction.create(
                reaction_type=data.reactionType,
                user_id=publisher,
                post_id=data.targetId,
            )
            reaction = await PostReaction.get_or_fail(
                reaction.uid, join=[PostReaction.user, PostReaction.post]
            )

        return self.get_response_dto(reaction)

    async def delete_reaction(
        self, uid: UUID, target_type: ReactionTargetType
    ) -> None:
        if target_type == 'comment':
            reaction = await CommentReaction.get(uid)
        else:
            reaction = await PostReaction.get(uid)

        if reaction:
            await reaction.delete()

    def get_response_dto(self, reaction: Reaction) -> ReactionResponseDTO:
        author = ReactionAuthorResponseDTO(
            username=reaction.user.username,
            firstName=reaction.user.first_name,
            lastName=reaction.user.last_name,
        )

        target = TargetResponseDTO(
            uid=(
                reaction.post.uid
                if isinstance(reaction, PostReaction)
                else reaction.comment.uid
            )
        )

        return ReactionResponseDTO(
            uid=reaction.uid,
            reactionType=reaction.reaction_type,
            reactedBy=author,
            reactedTo=target,
            targetType=(
                'post' if isinstance(reaction, PostReaction) else 'comment'
            ),
            reactedAt=reaction.created_at,
        )
