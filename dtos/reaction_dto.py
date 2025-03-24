from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from core.bases.base_dto import BaseRequestDTO, BaseResponseDTO
from models.db import Reactions

ReactionTargetType = Literal['comment', 'post']


class ReactionCreateRequestDTO(BaseRequestDTO):
    reactionType: Reactions = Field(
        title='Reaction type', description='Reaction type'
    )
    targetId: UUID = Field(title='Target ID', description='ID of the target.')
    targetType: ReactionTargetType = Field(
        title='Target type', description='Type of the reacted target.'
    )


class ReactionAuthorResponseDTO(BaseResponseDTO):
    username: str = Field(title='Username', description='Username')
    firstName: str = Field(title='First name', description='First name')
    lastName: str = Field(title='Last name', description='Last name')


class TargetResponseDTO(BaseResponseDTO):
    uid: UUID = Field(title='UID', description='ID of the target.')


class ReactionResponseDTO(BaseResponseDTO):
    uid: UUID = Field(title='UID', description='Reaction ID')
    reactionType: Reactions = Field(
        title='Reaction type', description='Reaction type'
    )
    reactedBy: ReactionAuthorResponseDTO = Field(
        title='Reacted by',
        description='User who reacted to the target.',
    )
    reactedTo: TargetResponseDTO = Field(
        title='Reacted to',
        description='Target that was reacted to.',
    )
    targetType: ReactionTargetType = Field(
        title='Target type',
        description='Type of the reacted target.',
    )
    reactedAt: datetime = Field(
        title='Reacted at',
        description='Date when the user reacted to the target.',
    )
