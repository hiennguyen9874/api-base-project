from typing import Annotated, TYPE_CHECKING, Union

from pydantic import Field
from pydantic.json_schema import SkipJsonSchema

if TYPE_CHECKING:
    from typing import Optional as OptionalField
    from typing import Optional as OptionalParam
else:

    class OptionalParam:
        # https://github.com/pydantic/pydantic/issues/6647#issuecomment-1646227125
        def __class_getitem__(cls, item):
            # return Annotated[
            #     Union[item, SkipJsonSchema[None]],
            #     Field(json_schema_extra=lambda x: x.pop("default", None)),
            # ]
            return Union[item, SkipJsonSchema[None]]

    class OptionalField:
        # https://github.com/pydantic/pydantic/issues/6647#issuecomment-1646227125
        def __class_getitem__(cls, item):
            return Annotated[
                Union[item, SkipJsonSchema[None]],
                Field(json_schema_extra=lambda x: x.pop("default", None)),
            ]
