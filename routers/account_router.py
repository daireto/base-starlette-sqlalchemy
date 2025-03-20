from core import I18N
from core.api.methods import delete, get, put
from core.api.responses import DTOResponse, EmptyResponse, ErrorResponse
from core.auth.decorator import auth
from core.auth.enums import Roles
from core.bases.base_router import BaseRouter
from dtos.user_dto import SelfUserUpdateRequestDTO, UserResponseDTO
from services.user_service import IUserService


@auth(Roles.USER)
class AccountRouter(BaseRouter):

    base_path = '/users/me'

    @get('/')
    async def get_current_user(
        self,
        service: IUserService,
        t: I18N,
    ) -> DTOResponse[UserResponseDTO] | ErrorResponse:
        """Gets the current user.

        ### Responses
        200 : UserResponseDTO
            Current user.
        404 : ErrorResponse
            User not found.
        """
        user = await service.get_user(self.request.user.uid)
        if user is None:
            return self.not_found(t('user.user_not_found'))

        return DTOResponse(user)

    @put('/')
    async def update_current_user(
        self,
        data: SelfUserUpdateRequestDTO,
        service: IUserService,
        t: I18N,
    ) -> DTOResponse[UserResponseDTO] | ErrorResponse:
        """Updates the current user.

        ### Responses
        200 : UserResponseDTO
            Updated user.
        404 : ErrorResponse
            User not found.
        """
        user = await service.update_user(
            self.request.user.uid, data, self.request.user.uid
        )
        if user is None:
            return self.not_found(t('user.user_not_found'))

        return DTOResponse(user)

    @delete('/')
    async def delete_current_user(
        self, service: IUserService
    ) -> EmptyResponse:
        """Deletes the current user.

        ### Responses
        204 : EmptyResponse
            User deleted.
        """
        await service.delete_user(self.request.user.uid)
        return EmptyResponse()
