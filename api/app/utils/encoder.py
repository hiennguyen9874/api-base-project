import datetime
import decimal
import uuid
from collections import OrderedDict
from typing import Any, Callable

from fastapi.encoders import jsonable_encoder
from fastapi.types import IncEx

__all__ = ["jsonable_encoder_sqlalchemy", "jsonable_encoder_cassandra"]


def jsonable_encoder_sqlalchemy(  # pylint: disable=too-many-arguments
    obj: Any,
    include: IncEx | None = None,
    exclude: IncEx | None = None,
    by_alias: bool = True,
    exclude_unset: bool = False,
    exclude_defaults: bool = False,
    exclude_none: bool = False,
    custom_encoder: dict[Any, Callable[[Any], Any]] | None = None,
    sqlalchemy_safe: bool = True,
) -> Any:
    sqlalchemy_custom_encoder = {
        bool: lambda x: x,
        bytes: lambda x: x,
        datetime.date: lambda x: x,
        datetime.datetime: lambda x: x,
        datetime.time: lambda x: x,
        datetime.timedelta: lambda x: x,
        decimal.Decimal: lambda x: x,
        float: lambda x: x,
        int: lambda x: x,
        str: lambda x: x,
        uuid.UUID: lambda x: x,
    }
    if custom_encoder is not None:
        sqlalchemy_custom_encoder = {**sqlalchemy_custom_encoder, **custom_encoder}
    return jsonable_encoder(
        obj=obj,
        include=include,
        exclude=exclude,
        by_alias=by_alias,
        exclude_unset=exclude_unset,
        exclude_defaults=exclude_defaults,
        exclude_none=exclude_none,
        custom_encoder=sqlalchemy_custom_encoder,
        sqlalchemy_safe=sqlalchemy_safe,
    )


def jsonable_encoder_cassandra(  # pylint: disable=too-many-arguments
    obj: Any,
    include: IncEx | None = None,
    exclude: IncEx | None = None,
    by_alias: bool = True,
    exclude_unset: bool = False,
    exclude_defaults: bool = False,
    exclude_none: bool = False,
    custom_encoder: dict[Any, Callable[[Any], Any]] | None = None,
    sqlalchemy_safe: bool = True,
) -> Any:
    cassandra_custom_encoder = {
        bool: lambda x: x,
        float: lambda x: x,
        int: lambda x: x,
        decimal.Decimal: lambda x: x,
        str: lambda x: x,
        uuid.UUID: lambda x: x,
        datetime.date: lambda x: x,
        datetime.datetime: lambda x: x,
        datetime.time: lambda x: x,
        list: lambda x: x,
        tuple: lambda x: x,
        set: lambda x: x,
        dict: lambda x: x,
        OrderedDict: lambda x: x,
    }
    if custom_encoder is not None:
        cassandra_custom_encoder = {**cassandra_custom_encoder, **custom_encoder}
    return jsonable_encoder(
        obj=obj,
        include=include,
        exclude=exclude,
        by_alias=by_alias,
        exclude_unset=exclude_unset,
        exclude_defaults=exclude_defaults,
        exclude_none=exclude_none,
        custom_encoder=cassandra_custom_encoder,
        sqlalchemy_safe=sqlalchemy_safe,
    )
