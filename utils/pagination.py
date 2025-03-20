"""This module provides pagination tools."""

import math
from typing import Generic, TypeVar

PaginationType = TypeVar('PaginationType')


def compute_skip(page: int, limit: int) -> int:
    """Compute the skip value.

    Parameters
    ----------
    page : int
        Page number.
    limit : int
        Limit.

    Returns
    -------
    int
        Skip value.
    """
    return limit * (page - 1)


def compute_pages_number(count: int, limit: int) -> int:
    """Compute the number of pages.

    Parameters
    ----------
    count : int
        Total number of items.
    limit : int
        Limit.

    Returns
    -------
    int
        Number of pages.
    """
    return math.ceil(count / limit) if limit else 1


class PaginatedResponse(Generic[PaginationType]):
    """Paginated response."""

    def __init__(
        self,
        data: list[PaginationType],
        page: int,
        skip: int,
        limit: int,
        count: int | None = None,
    ) -> None:
        """Creates a paginated response.

        Parameters
        ----------
        data : list[PaginationType]
            Paginated data.
        page : int
            Page number.
        skip : int
            Skip.
        limit : int
            Limit.
        count : int | None, optional
            Total number of items, by default None.
        """
        self.data = data
        self.page = page
        self.skip = skip
        self.limit = limit
        self.count = count
        self.pages = (
            compute_pages_number(self.count, self.limit)
            if self.count is not None
            else None
        )

    def to_response(self, serialize_data: bool = True) -> dict[str, object]:
        """Serialize response to dict.

        Parameters
        ----------
        serialize_data : bool, optional
            Whether to serialize data, by default True.

        Returns
        -------
        dict[str, object]
            Serialized response.
        """
        content: dict[str, object] = {
            'page': self.page,
            'skip': self.skip,
            'limit': self.limit,
        }

        if self.count is not None:
            content['count'] = self.count

        if self.pages is not None:
            content['pages'] = self.pages

        if serialize_data:
            content['data'] = self.data

        return content
