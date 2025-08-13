from typing import Annotated

from fastapi import Query
from fastapi_pagination import Params
from fastapi_pagination.bases import AbstractParams

__all__ = ["get_limit_offset", "get_params", "get_objects_params", "get_videos_params"]


def get_params(
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    size: Annotated[int, Query(ge=1, le=100, description="Page size")] = 50,
) -> Params:
    return Params(page=page, size=size)


def get_objects_params(
    response_objects_page: Annotated[int, Query(ge=1, description="Page objects number")] = 1,
    response_objects_size: Annotated[
        int, Query(ge=1, le=100, description="Page objects size")
    ] = 50,
) -> Params:
    return Params(page=response_objects_page, size=response_objects_size)


def get_videos_params(
    response_videos_page: Annotated[int, Query(ge=1, description="Page videos number")] = 1,
    response_videos_size: Annotated[int, Query(ge=1, le=100, description="Page videos size")] = 50,
) -> Params:
    return Params(page=response_videos_page, size=response_videos_size)


def get_limit_offset(params: AbstractParams) -> tuple[int, int]:
    raw_params = params.to_raw_params()
    limit, offset = raw_params.limit, raw_params.offset  # type: ignore
    return limit, offset
