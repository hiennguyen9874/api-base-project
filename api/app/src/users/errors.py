from app import errors

__all__ = [
    "user_not_found",
    "user_not_verified",
    "user_already_verified",
    "exists_email",
]


def user_not_found() -> errors.AppException:
    """Return a user not found error"""
    return errors.not_found("User not found")


def user_not_verified(msg: str) -> errors.AppException:
    """Return a user not verified error"""
    return errors.AppException(
        error_code=errors.ErrorCode.BAD_REQUEST,
        msg=msg,
        details={"error_type": "user_not_verified"},
    )


def user_already_verified(msg: str) -> errors.AppException:
    """Return a user already verified error"""
    return errors.AppException(
        error_code=errors.ErrorCode.BAD_REQUEST,
        msg=msg,
        details={"error_type": "user_already_verified"},
    )


def exists_email(msg: str) -> errors.AppException:
    """Return an email already exists error"""
    return errors.AppException(
        error_code=errors.ErrorCode.BAD_REQUEST,
        msg=msg,
        details={"error_type": "exists_email"},
    )
