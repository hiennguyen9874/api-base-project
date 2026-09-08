"""Safe fallbacks that make source imports possible without local configuration."""

from secrets import token_urlsafe


def ephemeral_development_secret() -> str:
    """Return a process-local placeholder which must not be used for deployment."""
    return token_urlsafe(32)
