from typing import Literal

from pydantic import Field

from core.bases.base_dto import BaseResponseDTO


class HealthResponseDTO(BaseResponseDTO):
    status: Literal['ok', 'error'] = Field(
        title='Status',
        description=(
            'Returns "ok" if the server is running without errors. '
            'Otherwise, returns "error".'
        ),
        default='ok',
    )
    authenticated: bool = Field(
        title='Authenticated',
        description='Whether the user is authenticated.',
        default=False,
    )
    message: str = Field(
        title='Message',
        description=(
            'Server status message. If an error occurs, returns '
            'the error message.'
        ),
        default='Server is running',
    )
