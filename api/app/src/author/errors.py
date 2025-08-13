from app import errors

__all__ = [
    "author_not_found",
    "author_already_exists",
]


def author_not_found(msg: str) -> errors.AppException:
    """Return an author not found error"""
    return errors.not_found(msg)


def author_already_exists(msg: str) -> errors.AppException:
    """Return an author already exists error"""
    return errors.AppException(
        error_code=errors.ErrorCode.BAD_REQUEST,
        msg=msg,
        details={"error_type": "author_already_exists"},
    )
