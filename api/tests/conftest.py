from __future__ import annotations

import os
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

API_ROOT = Path(__file__).resolve().parents[1]
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://test:test@localhost:5433/cashlens_test",
)

# The production YAML uses container paths. These values make app imports safe when
# pytest runs on the host and prevent tests from reporting to the configured Sentry.
# The shell's USER variable otherwise conflicts with the nested USER settings model.
os.environ.pop("USER", None)
os.environ.setdefault("APP__BASE_DIR", str(API_ROOT))
os.environ.setdefault("APP__CONFIG_DIR", str(API_ROOT / "tests" / "configs"))
os.environ.setdefault("APP__STATIC_DIR", str(API_ROOT / "app" / "static"))
os.environ.setdefault("SENTRY__DSN", "null")

from app.main import app  # noqa: E402
from app.src.db_models import Base  # noqa: E402
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


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def database_schema(engine: AsyncEngine) -> AsyncIterator[None]:
    """Create the metadata schema once, only when a test asks for database access."""
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


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
