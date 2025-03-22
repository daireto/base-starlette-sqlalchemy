from datetime import datetime
from uuid import UUID

from pydantic import Field

from core.bases.base_dto import BaseRequestDTO, BaseResponseDTO
from models.db import Reactions


class CommentRequestDTO(BaseRequestDTO):
    body: str = Field(title='Body', description='Body')
    post_id: UUID = Field(title='Post ID', description='Post ID')


class CommentCreateRequestDTO(CommentRequestDTO):
    pass


class CommentUpdateRequestDTO(CommentRequestDTO):
    pass


class CommentAuthorResponseDTO(BaseResponseDTO):
    username: str = Field(title='Username', description='Username')
    firstName: str = Field(title='First name', description='First name')
    lastName: str = Field(title='Last name', description='Last name')


class CommentPostResponseDTO(BaseResponseDTO):
    uid: UUID = Field(title='UID', description='Post ID')
    title: str = Field(title='Title', description='Title')


class RelatedReactionResponseDTO(BaseResponseDTO):
    uid: UUID = Field(title='UID', description='Comment reaction ID')
    reactionType: Reactions = Field(
        title='Reaction type', description='Reaction type'
    )


class CommentResponseDTO(BaseResponseDTO):
    uid: UUID = Field(title='UID', description='Comment ID')
    body: str = Field(title='Body', description='Body')
    tags: list[str] = Field(title='Tags', description='Tags')
    user: CommentAuthorResponseDTO = Field(
        title='Commented by',
        description='User who created the comment.',
    )
    post: CommentPostResponseDTO = Field(
        title='Commented on',
        description='Post that was commented on.',
    )
    reactions: list[RelatedReactionResponseDTO] = Field(
        title='Reactions',
        description='Comment reactions.',
        default=[],
    )
    updatedAt: datetime = Field(
        title='Updated at',
        description='Date when the comment was last updated.',
    )
