from typing import Any


def parse_cors_origin(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


def parse_trusted_host(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)
