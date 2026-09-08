from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator, Callable
from pathlib import Path

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

API_ROOT = Path(__file__).resolve().parents[1]
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://test:test@localhost:5433/cashlens_test",
)

# The production YAML uses container paths. These values make app imports safe when
# pytest runs on the host and prevent tests from reporting to the configured Sentry.
os.environ.setdefault("APP__BASE_DIR", str(API_ROOT))
os.environ.setdefault("APP__CONFIG_DIR", str(API_ROOT / "tests" / "configs"))
os.environ.setdefault("APP__STATIC_DIR", str(API_ROOT / "app" / "static"))
os.environ.setdefault("APP__TRUSTED_HOST", "test,localhost,127.0.0.1")
os.environ.setdefault("SENTRY__DSN", "null")
os.environ.setdefault("APP__SECRET_KEY", "test-app-secret-at-least-thirty-two-characters")
os.environ.setdefault(
    "TOKEN__ACCESS_TOKEN_SECRET_KEY", "test-access-secret-at-least-thirty-two-characters"
)
os.environ.setdefault(
    "TOKEN__REFRESH_TOKEN_SECRET_KEY", "test-refresh-secret-at-least-thirty-two-characters"
)
os.environ.setdefault("POSTGRES__USER", "test")
os.environ.setdefault("POSTGRES__PASSWORD", "test")
os.environ.setdefault("POSTGRES__DB", "cashlens_test")
os.environ.setdefault("TASKIQ__BROKER_URL", "amqp://guest:guest@localhost:5672")
os.environ.setdefault("TASKIQ__RESULT_BACKEND", "redis://localhost:6379/0")
os.environ.setdefault("USER__FIRST_USER_EMAIL", "owner@example.com")
os.environ.setdefault("USER__FIRST_USER_PASSWORD", "test-owner-password")

from app.main import app  # noqa: E402
from app.src.dependencies import get_db  # noqa: E402


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def engine() -> AsyncIterator[AsyncEngine]:
    """Create the test engine without sharing pooled connections across event loops."""
    test_engine = create_async_engine(
        TEST_DATABASE_URL,
        pool_pre_ping=True,
        poolclass=NullPool,
    )
    yield test_engine
    await test_engine.dispose()


def _migration_config(database_url: str) -> Config:
    config = Config(str(API_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(API_ROOT / "app" / "alembic"))
    config.set_main_option(
        "sqlalchemy.url",
        make_url(database_url)
        .set(drivername="postgresql+psycopg2")
        .render_as_string(hide_password=False),
    )
    return config


def _upgrade_database(database_url: str) -> None:
    command.upgrade(_migration_config(database_url), "head")


@pytest.fixture
def migration_config() -> Callable[[str], Config]:
    """Build Alembic configuration pointing at an isolated PostgreSQL database."""
    return _migration_config


@pytest.fixture
def test_database_url() -> str:
    return TEST_DATABASE_URL


async def _reset_database(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.exec_driver_sql("DROP EXTENSION IF EXISTS unaccent CASCADE")
        await connection.exec_driver_sql("DROP EXTENSION IF EXISTS pg_trgm CASCADE")
        await connection.exec_driver_sql("DROP SCHEMA IF EXISTS public CASCADE")
        await connection.exec_driver_sql("CREATE SCHEMA public")


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def database_schema(engine: AsyncEngine) -> AsyncIterator[None]:
    """Apply production migrations once for PostgreSQL-backed tests."""
    await _reset_database(engine)
    await asyncio.to_thread(_upgrade_database, TEST_DATABASE_URL)
    yield
    await _reset_database(engine)


@pytest.fixture
async def db_session(
    engine: AsyncEngine,
    database_schema: None,
) -> AsyncIterator[AsyncSession]:
    """Run each database test in an outer transaction that is always rolled back."""
    del database_schema
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()


@pytest.fixture
async def asgi_client() -> AsyncIterator[AsyncClient]:
    """Provide an in-process HTTP client without starting external-service lifespan hooks."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    """Provide an HTTP client whose database dependency uses the isolated test session."""

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)
