from core import I18N
from core.api.methods import post
from core.api.responses import DTOResponse, ErrorResponse
from core.bases.base_router import BaseRouter
from dtos.auth_dto import LoginRequestDTO, LoginResponseDTO, SignupRequestDTO
from services.auth_service import IAuthService


class AuthRouter(BaseRouter):

    base_path = '/auth'

    @post('/login')
    async def login(
        self, data: LoginRequestDTO, service: IAuthService, t: I18N
    ) -> DTOResponse[LoginResponseDTO] | ErrorResponse:
        """Performs the login with the provided credentials.

        ### Responses
        200 : LoginResponseDTO
            Access token.
        401 : ErrorResponse.
            Incorrect credentials.
        """
        access_token = await service.login(data)
        if access_token is None:
            return ErrorResponse(
                t('auth.incorrect_credentials'), status_code=401
            )

        return DTOResponse(LoginResponseDTO(accessToken=access_token))

    @post('/signup')
    async def signup(
        self, data: SignupRequestDTO, service: IAuthService
    ) -> DTOResponse[LoginResponseDTO] | ErrorResponse:
        """Signs up a new user.

        ### Responses
        201 : LoginResponseDTO
            Access token.

            User signed up successfully.
        """
        access_token = await service.signup(data)
        return DTOResponse(
            LoginResponseDTO(accessToken=access_token), status_code=201
        )
