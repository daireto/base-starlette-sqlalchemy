from datetime import datetime

from pydantic import Field, field_validator

from core.bases.base_dto import BaseRequestDTO, BaseResponseDTO


class LoginRequestDTO(BaseRequestDTO):
    username: str = Field(title='Username', description='Username')
    password: str = Field(title='Password', description='Password')

    @field_validator('username')
    def username_lower(cls, v: str):
        return v.lower()


class SignupRequestDTO(BaseRequestDTO):
    username: str = Field(
        title='Username', description='Username', max_length=15
    )
    firstName: str = Field(
        title='First name', description='First name', max_length=50
    )
    lastName: str = Field(
        title='Last name', description='Last name', max_length=50
    )
    email: str = Field(title='Email', description='Email', max_length=70)
    birthday: datetime = Field(title='Birthday', description='Birthday')
    password: str = Field(
        title='Password', description='Password', min_length=8, max_length=24
    )
    confirmPassword: str = Field(
        title='Confirm password', description='Confirm password'
    )

    @field_validator('username')
    def username_lower(cls, v: str):
        return v.lower()


class LoginResponseDTO(BaseResponseDTO):
    accessToken: str = Field(title='Access token')
