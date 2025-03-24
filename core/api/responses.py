"""This module provides different response classes."""

from collections.abc import Mapping
from typing import Any, Generic, TypeVar

import orjson
from pydantic import ValidationError
from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import JSONResponse as StarletteJSONResponse
from starlette.responses import Response

from core.bases.base_dto import BaseResponseDTO
from utils.func import build_odata_response_body
from utils.pagination import PaginatedResponse

from .errors import HTTPError

ResponseDTO = TypeVar('ResponseDTO', bound=BaseResponseDTO)


class JSONResponse(StarletteJSONResponse):
    """This class provides a custom JSON response class.
    using the ``orjson`` library.
    """

    def render(self, content: Any) -> bytes:
        return orjson.dumps(content, default=str)


class DTOResponse(Generic[ResponseDTO], JSONResponse):
    """Response class for DTOs."""

    def __init__(
        self,
        data: ResponseDTO | list[ResponseDTO],
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        if isinstance(data, list):
            response_data = [element.to_response() for element in data]
        else:
            response_data = data.to_response()
        super(JSONResponse, self).__init__(
            response_data, status_code, headers, media_type, background
        )


class PaginationDTOResponse(Generic[ResponseDTO], JSONResponse):
    """Response class for paginated DTOs."""

    def __init__(
        self,
        data: PaginatedResponse[ResponseDTO],
        request: Request,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        if request.query_params.get('responseType', '') == 'odata':
            content = build_odata_response_body(
                request_url=str(request.url),
                data=[element.to_response() for element in data.data],
                count=data.count,
            )
        else:
            content = data.to_response(serialize_data=False)
            content['data'] = [element.to_response() for element in data.data]

        super(JSONResponse, self).__init__(
            content, status_code, headers, media_type, background
        )


class ErrorResponse(JSONResponse):
    """Response class for errors."""

    def __init__(
        self,
        error: str | Exception,
        status_code: int = 500,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        if isinstance(error, ValidationError):
            content = {'errors': error.errors(include_url=False)}
        elif isinstance(error, HTTPError):
            content = {'message': error.message}
            status_code = error.status_code
        else:
            content = {
                'message': (
                    str(error) if isinstance(error, Exception) else error
                ),
            }
        super().__init__(content, status_code, headers, media_type, background)


class EmptyResponse(Response):
    """Empty response class."""

    def __init__(
        self,
        status_code: int = 204,
        headers: Mapping[str, str] | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        super().__init__(None, status_code, headers, None, background)
