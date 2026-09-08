# syntax=docker/dockerfile:1.7

FROM python:3.10-slim AS runtime-base

ARG DEBIAN_FRONTEND=noninteractive

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON=3.10 \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH=/app/.venv/bin:$PATH \
    PYTHONPATH=/app

WORKDIR /app

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl libmagic1 libpq5 libjemalloc2 && \
    rm -rf /var/lib/apt/lists/*

FROM runtime-base AS builder-base

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
      build-essential clang gcc libc-dev libpq-dev libssl-dev && \
    rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.5.10 /uv /uvx /bin/
COPY pyproject.toml uv.lock ./

FROM builder-base AS builder-production
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev --no-editable

FROM builder-base AS builder-development
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-editable

FROM runtime-base AS development
COPY --from=builder-development /app/.venv /app/.venv
COPY alembic.ini ./
COPY app ./app
COPY scripts/prestart.sh /prestart.sh
RUN chmod 0755 /prestart.sh

FROM runtime-base AS production
RUN groupadd --gid 10001 cashlens && \
    useradd --uid 10001 --gid cashlens --create-home cashlens && \
    mkdir -p /app/media /var/log/cashlens && \
    chown -R cashlens:cashlens /app /app/media /var/log/cashlens

COPY --from=builder-production --chown=cashlens:cashlens /app/.venv /app/.venv
COPY --chown=cashlens:cashlens alembic.ini ./
COPY --chown=cashlens:cashlens app ./app
COPY --chown=cashlens:cashlens scripts/prestart.sh /prestart.sh
RUN chmod 0755 /prestart.sh

USER cashlens
