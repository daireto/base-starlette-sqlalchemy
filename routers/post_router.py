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
from dtos.post_dto import (
    PostCreateRequestDTO,
    PostResponseDTO,
    PostUpdateRequestDTO,
)
from services.post_service import IPostService


@auth(Roles.ADMIN)
class PostRouter(BaseRouter):

    base_path = '/posts'

    @get('/')
    @use_odata
    async def list_posts(
        self, service: IPostService
    ) -> PaginationDTOResponse[PostResponseDTO]:
        """Gets a paginated list of posts.

        ### Responses
        200 : PaginationDTOResponse[PostResponseDTO]
            Paginated list of posts.
        """
        odata_options = self.parse_odata()
        posts = await service.list_posts(odata_options)
        return PaginationDTOResponse(posts, self.request)

    @post('/')
    async def create_post(
        self,
        data: PostCreateRequestDTO,
        service: IPostService,
    ) -> DTOResponse[PostResponseDTO]:
        """Creates a new post.

        ### Responses
        201 : DTOResponse[PostResponseDTO]
            Created post.
        """
        post = await service.create_post(data, self.request.user.uid)
        return DTOResponse(post, status_code=201)

    @get('/{uid:str}')
    async def get_post(
        self,
        uid: str,
        service: IPostService,
        t: I18N,
    ) -> DTOResponse[PostResponseDTO] | ErrorResponse:
        """Gets the post with the provided ID.

        ### Parameters
        uid : str
            Post ID.

        ### Responses
        200 : DTOResponse[PostResponseDTO]
            Post.
        404 : ErrorResponse
            Post not found.
        """
        post = await service.get_post(uid)
        if post is None:
            return self.not_found(t('post.post_not_found'))

        return DTOResponse(post)

    @put('/{uid:str}')
    async def update_post(
        self,
        uid: str,
        data: PostUpdateRequestDTO,
        service: IPostService,
        t: I18N,
    ) -> DTOResponse[PostResponseDTO] | ErrorResponse:
        """Updates the post with the provided ID.

        ### Parameters
        uid : str
            Post ID.

        ### Responses
        200 : DTOResponse[PostResponseDTO]
            Updated post.
        404 : ErrorResponse
            Post not found.
        """
        post = await service.update_post(uid, data)
        if post is None:
            return self.not_found(t('post.post_not_found'))

        return DTOResponse(post)

    @delete('/{uid:str}')
    async def delete_post(
        self,
        uid: str,
        service: IPostService,
    ) -> EmptyResponse:
        """Deletes the post with the provided ID.

        ### Parameters
        uid : str
            Post ID.

        ### Responses
        204 : EmptyResponse
            Post deleted.
        """
        await service.delete_post(uid)
        return EmptyResponse()
