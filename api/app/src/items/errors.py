from app import errors

__all__ = ["item_not_found"]


def item_not_found() -> errors.AppException:
    """Return an item not found error"""
    return errors.not_found("Item not found")
