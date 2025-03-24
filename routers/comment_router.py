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
from dtos.comment_dto import (
    CommentCreateRequestDTO,
    CommentResponseDTO,
    CommentUpdateRequestDTO,
)
from services.comment_service import ICommentService


@auth(Roles.ADMIN)
class CommentRouter(BaseRouter):

    base_path = '/comments'

    @get('/')
    @use_odata
    async def list_comments(
        self, service: ICommentService
    ) -> PaginationDTOResponse[CommentResponseDTO]:
        """Gets a paginated list of comments.

        ### Responses
        200 : PaginationDTOResponse[CommentResponseDTO]
            Paginated list of comments.
        """
        odata_options = self.parse_odata()
        comments = await service.list_comments(odata_options)
        return PaginationDTOResponse(comments, self.request)

    @post('/')
    async def create_comment(
        self,
        data: CommentCreateRequestDTO,
        service: ICommentService,
    ) -> DTOResponse[CommentResponseDTO]:
        """Creates a new comment.

        ### Responses
        201 : DTOResponse[CommentResponseDTO]
            Created comment.
        """
        comment = await service.create_comment(data, self.request.user.uid)
        return DTOResponse(comment, status_code=201)

    @get('/{uid:str}')
    async def get_comment(
        self,
        uid: str,
        service: ICommentService,
        t: I18N,
    ) -> DTOResponse[CommentResponseDTO] | ErrorResponse:
        """Gets the comment with the provided ID.

        ### Parameters
        uid : str
            Comment ID.

        ### Responses
        200 : DTOResponse[CommentResponseDTO]
            Comment.
        404 : ErrorResponse
            Comment not found.
        """
        comment = await service.get_comment(uid)
        if comment is None:
            return self.not_found(t('comment.comment_not_found'))

        return DTOResponse(comment)

    @put('/{uid:str}')
    async def update_comment(
        self,
        uid: str,
        data: CommentUpdateRequestDTO,
        service: ICommentService,
        t: I18N,
    ) -> DTOResponse[CommentResponseDTO] | ErrorResponse:
        """Updates the comment with the provided ID.

        ### Parameters
        uid : str
            Comment ID.

        ### Responses
        200 : DTOResponse[CommentResponseDTO]
            Updated comment.
        404 : ErrorResponse
            Comment not found.
        """
        comment = await service.update_comment(uid, data)
        if comment is None:
            return self.not_found(t('comment.comment_not_found'))

        return DTOResponse(comment)

    @delete('/{uid:str}')
    async def delete_comment(
        self,
        uid: str,
        service: ICommentService,
    ) -> EmptyResponse:
        """Deletes the comment with the provided ID.

        ### Parameters
        uid : str
            Comment ID.

        ### Responses
        204 : EmptyResponse
            Comment deleted.
        """
        await service.delete_comment(uid)
        return EmptyResponse()
