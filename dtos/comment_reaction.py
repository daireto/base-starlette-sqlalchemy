from datetime import datetime
from uuid import UUID

from pydantic import Field

from core.bases.base_dto import BaseRequestDTO, BaseResponseDTO
from models.db import Reactions


class CommentReactionRequestDTO(BaseRequestDTO):
    reactionType: Reactions = Field(
        title='Reaction type', description='Reaction type'
    )
    comment_id: UUID = Field(title='Comment ID', description='Comment ID')


class CommentReactionCreateRequestDTO(CommentReactionRequestDTO):
    pass


class CommentReactionUpdateRequestDTO(CommentReactionRequestDTO):
    pass


class CommentReactionAuthorResponseDTO(BaseResponseDTO):
    username: str = Field(title='Username', description='Username')
    firstName: str = Field(title='First name', description='First name')
    lastName: str = Field(title='Last name', description='Last name')


class ReactedCommentResponseDTO(BaseResponseDTO):
    uid: UUID = Field(title='UID', description='Comment ID')
    title: str = Field(title='Title', description='Title')


class CommentReactionResponseDTO(BaseResponseDTO):
    uid: UUID = Field(title='UID', description='Comment ID')
    reactionType: Reactions = Field(
        title='Reaction type', description='Reaction type'
    )
    user: CommentReactionAuthorResponseDTO = Field(
        title='Reacted by',
        description='User who reacted to the comment.',
    )
    comment: ReactedCommentResponseDTO = Field(
        title='Reacted to',
        description='Comment that was reacted to.',
    )
    createdAt: datetime = Field(
        title='Created at',
        description='Date when the reaction was created.',
    )
