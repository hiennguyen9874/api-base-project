from app import errors

__all__ = [
    "not_authenticated",
    "invalid_jwt_token",
    "invalid_jwt_claims",
    "token_not_found",
    "refresh_token_not_set",
    "refresh_token_not_found",
    "invalid_reset_password_token",
    "expired_jwt_token",
    "inactive_user",
    "wrong_password",
]


def not_authenticated(msg: str) -> errors.AppException:
    """Return a not authenticated error"""
    return errors.AppException(
        error_code=errors.ErrorCode.UNAUTHORIZED,
        msg=msg,
    )


def invalid_jwt_token(msg: str) -> errors.AppException:
    """Return an invalid JWT token error"""
    return errors.AppException(
        error_code=errors.ErrorCode.UNAUTHORIZED,
        msg=msg,
    )


def invalid_jwt_claims(msg: str) -> errors.AppException:
    """Return an invalid JWT claims error"""
    return errors.AppException(
        error_code=errors.ErrorCode.UNAUTHORIZED,
        msg=msg,
    )


def token_not_found(msg: str) -> errors.AppException:
    """Return a token not found error"""
    return errors.AppException(
        error_code=errors.ErrorCode.UNAUTHORIZED,
        msg=msg,
    )


def invalid_reset_password_token(msg: str) -> errors.AppException:
    """Return an invalid reset password token error"""
    return errors.AppException(
        error_code=errors.ErrorCode.UNAUTHORIZED,
        msg=msg,
    )


def refresh_token_not_set(msg: str) -> errors.AppException:
    """Return a refresh token not set error"""
    return errors.AppException(
        error_code=errors.ErrorCode.UNAUTHORIZED,
        msg=msg,
    )


def refresh_token_not_found(msg: str) -> errors.AppException:
    """Return a refresh token not found error"""
    return errors.AppException(
        error_code=errors.ErrorCode.UNAUTHORIZED,
        msg=msg,
    )


def expired_jwt_token(msg: str) -> errors.AppException:
    """Return an expired JWT token error"""
    return errors.AppException(
        error_code=errors.ErrorCode.UNAUTHORIZED,
        msg=msg,
    )


def inactive_user(msg: str) -> errors.AppException:
    """Return an inactive user error"""
    return errors.AppException(
        error_code=errors.ErrorCode.FORBIDDEN,
        msg=msg,
    )


def wrong_password(msg: str) -> errors.AppException:
    """Return a wrong password error"""
    return errors.AppException(
        error_code=errors.ErrorCode.UNAUTHORIZED,
        msg=msg,
    )
