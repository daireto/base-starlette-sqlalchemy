from uuid import UUID

from core import I18N
from core.api.methods import delete, get, post, put
from core.api.odata import use_odata
from core.api.responses import (
    DTOResponse,
    EmptyResponse,
    ErrorResponse,
    PaginationDTOResponse,
)
from core.auth.decorator import auth
from core.auth.enums import Roles
from core.bases.base_router import BaseRouter
from dtos.user_dto import (
    UserCreateRequestDTO,
    UserResponseDTO,
    UserUpdateRequestDTO,
)
from services.user_service import IUserService


@auth(Roles.ADMIN)
class UserRouter(BaseRouter):

    base_path = '/users'

    @get('/')
    @use_odata
    async def list_users(
        self, service: IUserService
    ) -> PaginationDTOResponse[UserResponseDTO]:
        """Gets a paginated list of users.

        ### Responses
        200 : PaginationDTOResponse[UserResponseDTO]
            Paginated list of users.
        """
        odata_options = self.parse_odata()
        users = await service.list_users(odata_options)
        return PaginationDTOResponse(users, self.request)

    @post('/')
    async def create_user(
        self,
        data: UserCreateRequestDTO,
        service: IUserService,
    ) -> DTOResponse[UserResponseDTO]:
        """Creates a new user.

        ### Responses
        201 : DTOResponse[UserResponseDTO]
            Created user.
        """
        user = await service.create_user(data, self.request.user.uid)
        return DTOResponse(user, status_code=201)

    @get('/{uid:uuid}')
    async def get_user(
        self,
        uid: UUID,
        service: IUserService,
        t: I18N,
    ) -> DTOResponse[UserResponseDTO] | ErrorResponse:
        """Gets the user with the provided ID.

        ### Parameters
        uid : UUID
            User ID.

        ### Responses
        200 : DTOResponse[UserResponseDTO]
            User.
        404 : ErrorResponse
            User not found.
        """
        user = await service.get_user(uid)
        if user is None:
            return self.not_found(t('user.user_not_found'))

        return DTOResponse(user)

    @get('/{username_or_email:str}')
    async def get_user_by_username_or_email(
        self,
        username_or_email: str,
        service: IUserService,
        t: I18N,
    ) -> DTOResponse[UserResponseDTO] | ErrorResponse:
        """Gets the user with the provided username or email.

        ### Parameters
        username_or_email : str
            Username or email.

        ### Responses
        200 : DTOResponse[UserResponseDTO]
            User.
        404 : ErrorResponse
            User not found.
        """
        user = await service.get_user_by_username_or_email(username_or_email)
        if user is None:
            return self.not_found(t('user.user_not_found'))

        return DTOResponse(user)

    @put('/{uid:uuid}')
    async def update_user(
        self,
        uid: UUID,
        data: UserUpdateRequestDTO,
        service: IUserService,
        t: I18N,
    ) -> DTOResponse[UserResponseDTO] | ErrorResponse:
        """Updates the user with the provided ID.

        ### Parameters
        uid : UUID
            User ID.

        ### Responses
        200 : DTOResponse[UserResponseDTO]
            Updated user.
        404 : ErrorResponse
            User not found.
        """
        user = await service.update_user(uid, data, self.request.user.uid)
        if user is None:
            return self.not_found(t('user.user_not_found'))

        return DTOResponse(user)

    @delete('/{uid:uuid}')
    async def delete_user(
        self,
        uid: UUID,
        service: IUserService,
    ) -> EmptyResponse:
        """Deletes the user with the provided ID.

        ### Parameters
        uid : UUID
            User ID.

        ### Responses
        204 : EmptyResponse
            User deleted.
        """
        await service.delete_user(uid)
        return EmptyResponse()
