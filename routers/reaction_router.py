from core import I18N
from core.api.methods import delete, get, post
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
from dtos.reaction_dto import (
    ReactionCreateRequestDTO,
    ReactionResponseDTO,
)
from services.reaction_service import IReactionService


@auth(Roles.ADMIN)
class ReactionRouter(BaseRouter):

    base_path = '/reactions'

    @get('/posts/')
    @use_odata
    async def list_post_reactions(
        self, service: IReactionService
    ) -> PaginationDTOResponse[ReactionResponseDTO]:
        """Gets a paginated list of post reactions.

        ### Responses
        200 : PaginationDTOResponse[ReactionResponseDTO]
            Paginated list of post reactions.
        """
        odata_options = self.parse_odata()
        reactions = await service.list_reactions(odata_options, 'post')
        return PaginationDTOResponse(reactions, self.request)

    @get('/comments/')
    @use_odata
    async def list_comment_reactions(
        self, service: IReactionService
    ) -> PaginationDTOResponse[ReactionResponseDTO]:
        """Gets a paginated list of comment reactions.

        ### Responses
        200 : PaginationDTOResponse[ReactionResponseDTO]
            Paginated list of comment reactions.
        """
        odata_options = self.parse_odata()
        reactions = await service.list_reactions(odata_options, 'comment')
        return PaginationDTOResponse(reactions, self.request)

    @post('/')
    async def create_reaction(
        self,
        data: ReactionCreateRequestDTO,
        service: IReactionService,
    ) -> DTOResponse[ReactionResponseDTO]:
        """Creates a new reaction.

        ### Responses
        201 : DTOResponse[ReactionResponseDTO]
            Created reaction.
        """
        reaction = await service.create_reaction(data, self.request.user.uid)
        return DTOResponse(reaction, status_code=201)

    @get('/posts/{uid:str}')
    async def get_post_reaction(
        self,
        uid: str,
        service: IReactionService,
        t: I18N,
    ) -> DTOResponse[ReactionResponseDTO] | ErrorResponse:
        """Gets the post reaction with the provided ID.

        ### Parameters
        uid : str
            Reaction ID.

        ### Responses
        200 : DTOResponse[ReactionResponseDTO]
            Post reaction.
        404 : ErrorResponse
            Reaction not found.
        """
        reaction = await service.get_reaction(uid, 'post')
        if reaction is None:
            return self.not_found(t('reaction.reaction_not_found'))

        return DTOResponse(reaction)

    @get('/comments/{uid:str}')
    async def get_comment_reaction(
        self,
        uid: str,
        service: IReactionService,
        t: I18N,
    ) -> DTOResponse[ReactionResponseDTO] | ErrorResponse:
        """Gets the comment reaction with the provided ID.

        ### Parameters
        uid : str
            Reaction ID.

        ### Responses
        200 : DTOResponse[ReactionResponseDTO]
            Comment reaction.
        404 : ErrorResponse
            Reaction not found.
        """
        reaction = await service.get_reaction(uid, 'comment')
        if reaction is None:
            return self.not_found(t('reaction.reaction_not_found'))

        return DTOResponse(reaction)

    @delete('/posts/{uid:str}')
    async def delete_post_reaction(
        self,
        uid: str,
        service: IReactionService,
    ) -> EmptyResponse:
        """Deletes the post reaction with the provided ID.

        ### Parameters
        uid : str
            Reaction ID.

        ### Responses
        204 : EmptyResponse
            Reaction deleted.
        """
        await service.delete_reaction(uid, 'post')
        return EmptyResponse()

    @delete('/comments/{uid:str}')
    async def delete_comment_reaction(
        self,
        uid: str,
        service: IReactionService,
    ) -> EmptyResponse:
        """Deletes the comment reaction with the provided ID.

        ### Parameters
        uid : str
            Reaction ID.

        ### Responses
        204 : EmptyResponse
            Reaction deleted.
        """
        await service.delete_reaction(uid, 'comment')
        return EmptyResponse()
