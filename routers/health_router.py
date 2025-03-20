from core.api.methods import get
from core.api.responses import DTOResponse
from core.bases.base_router import BaseRouter
from core.settings import Settings
from dtos.health_dto import HealthResponseDTO


class HealthRouter(BaseRouter):

    @get('/health')
    async def health(self) -> DTOResponse[HealthResponseDTO]:
        """Gets the health of the server.

        ### Responses
        200 : HealthResponseDTO
            Server status.
        """
        health = HealthResponseDTO(
            status=Settings.status.status,
            authenticated=self.request.user.is_authenticated,
            message=Settings.status.message,
        )
        return DTOResponse(health)
