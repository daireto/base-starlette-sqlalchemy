"""This module provides the ``BaseService`` class
to define services.
"""

from abc import ABC
from typing import TypeVar

from odata_v4_query import ODataQueryOptions
from odata_v4_query.utils.sqlalchemy import apply_to_sqlalchemy_query
from sqlactive.async_query import AsyncQuery

from core.api.request import Request
from utils.pagination import PaginatedResponse, PaginationType

from .base_model import BaseModel

ModelType = TypeVar('ModelType', bound=BaseModel)


class BaseService(ABC):
    """Base class for services."""

    request: Request

    async def get_odata_count(self, odata_options: ODataQueryOptions, query: AsyncQuery[ModelType]) -> int | None:
        """Gets the number of items in the query
        if the ``$count`` option is set to ``True``.

        Parameters
        ----------
        query : AsyncQuery[ModelType]
            Async query.

        Returns
        -------
        int
            Number of items.
        None
            If the ``$count`` option is not set or is set to ``False``.
        """
        if not odata_options.count:
            return None

        return await query.skip(0).limit(0).count()

    def get_async_query(
        self, odata_options: ODataQueryOptions, model: type[ModelType]
    ) -> AsyncQuery[ModelType]:
        """Gets an async query for the given model from
        the given OData options.

        Parameters
        ----------
        odata_options : ODataQueryOptions
            OData query options.
        model : type[ModelType]
            DB Model.

        Returns
        -------
        AsyncQuery[ModelType]
            Async query.
        """
        query = AsyncQuery(apply_to_sqlalchemy_query(odata_options, model))
        if odata_options.search:
            query.search(odata_options.search)

        return query

    def to_paginated_response(
        self,
        odata_options: ODataQueryOptions,
        data: list[PaginationType],
        count: int | None = None,
    ) -> PaginatedResponse[PaginationType]:
        """Gets a paginated response.

        Parameters
        ----------
        odata_options : ODataQueryOptions
            OData query options.
        data : list[PaginationType]
            Paginated data.
        count : int, optional
            Total number of items, by default None.

        Returns
        -------
        PaginatedResponse[PaginationType]
            Paginated response.
        """
        return PaginatedResponse(
            data=data,
            page=odata_options.page or 1,
            skip=odata_options.skip or 0,
            limit=odata_options.top or 0,
            count=count,
        )
