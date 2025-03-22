from datetime import datetime
from uuid import UUID

from pydantic import Field

from core.bases.base_dto import BaseRequestDTO, BaseResponseDTO
from models.db import Reactions


class PostReactionRequestDTO(BaseRequestDTO):
    reactionType: Reactions = Field(
        title='Reaction type', description='Reaction type'
    )
    post_id: UUID = Field(title='Post ID', description='Post ID')


class PostReactionCreateRequestDTO(PostReactionRequestDTO):
    pass


class PostReactionUpdateRequestDTO(PostReactionRequestDTO):
    pass


class PostReactionAuthorResponseDTO(BaseResponseDTO):
    username: str = Field(title='Username', description='Username')
    firstName: str = Field(title='First name', description='First name')
    lastName: str = Field(title='Last name', description='Last name')


class ReactedPostResponseDTO(BaseResponseDTO):
    uid: UUID = Field(title='UID', description='Post ID')
    title: str = Field(title='Title', description='Title')


class PostReactionResponseDTO(BaseResponseDTO):
    uid: UUID = Field(title='UID', description='Comment ID')
    reactionType: Reactions = Field(
        title='Reaction type', description='Reaction type'
    )
    user: PostReactionAuthorResponseDTO = Field(
        title='Reacted by',
        description='User who reacted to the post.',
    )
    post: ReactedPostResponseDTO = Field(
        title='Reacted to',
        description='Post that was reacted to.',
    )
    createdAt: datetime = Field(
        title='Created at',
        description='Date when the reaction was created.',
    )
