from datetime import datetime
from uuid import UUID

from pydantic import Field

from core.bases.base_dto import BaseRequestDTO, BaseResponseDTO
from models.db import Reactions


class PostRequestDTO(BaseRequestDTO):
    title: str = Field(title='Title', description='Title', max_length=120)
    body: str = Field(title='Body', description='Body')
    tags: list[str] = Field(title='Tags', description='Tags')


class PostCreateRequestDTO(PostRequestDTO):
    pass


class PostUpdateRequestDTO(PostRequestDTO):
    pass


class PublisherResponseDTO(BaseResponseDTO):
    username: str = Field(title='Username', description='Username')
    firstName: str = Field(title='First name', description='First name')
    lastName: str = Field(title='Last name', description='Last name')


class RelatedCommentResponseDTO(BaseResponseDTO):
    uid: UUID = Field(title='UID', description='Comment ID')
    body: str = Field(title='Body', description='Body')


class RelatedReactionResponseDTO(BaseResponseDTO):
    uid: UUID = Field(title='UID', description='Post reaction ID')
    reactionType: Reactions = Field(
        title='Reaction type', description='Reaction type'
    )


class PostResponseDTO(BaseResponseDTO):
    uid: UUID = Field(title='UID', description='Post ID')
    title: str = Field(title='Title', description='Title')
    body: str = Field(title='Body', description='Body')
    tags: list[str] = Field(title='Tags', description='Tags')
    publisher: PublisherResponseDTO = Field(
        title='Created by',
        description='User who published the post.',
    )
    publishedAt: datetime = Field(
        title='Published at',
        description='Date when the post was published.',
    )
    comments: list[RelatedCommentResponseDTO] = Field(
        title='Comments',
        description='Comments created on the post.',
        default=[],
    )
    reactions: list[RelatedReactionResponseDTO] = Field(
        title='Reactions',
        description='Post reactions.',
        default=[],
    )
    updatedAt: datetime = Field(
        title='Updated at',
        description='Date when the post was last updated.',
    )
