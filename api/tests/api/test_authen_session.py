"""HTTP contract for the cookie-based CashLens session (#24).

Exercises login, current-user verification, refresh rotation, and logout through
the ASGI app with a transaction-wrapped database session and an in-memory Redis
double for the refresh-token store.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime, timedelta, timezone
from typing import Any, cast

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.security import create_token
from app.core.ratelimit import limiter
from app.core.settings import settings
from app.main import app
from app.src.authen.refresh_token_repository import refresh_token_repository
from app.src.dependencies import get_async_cache, get_db
from app.src.users.db_models import User
from app.src.users.schemas import UserCreate
from app.src.users.services import user_service


class FakeTokenStore:
    """Redis double covering the sorted-set commands RefreshTokenRepository uses."""

    def __init__(self) -> None:
        self.zsets: dict[str, dict[str, float]] = {}

    def pipeline(self, transaction: bool = True) -> FakeTokenStore.Pipeline:
        del transaction
        return FakeTokenStore.Pipeline(self)

    async def delete(self, key: str) -> None:
        self.zsets.pop(key, None)

    def _zadd(self, key: str, mapping: dict[str, float], gt: bool) -> int:
        zset = self.zsets.setdefault(key, {})
        added = 0
        for member, score in mapping.items():
            current = zset.get(member)
            if current is None or (gt and score > current) or not gt:
                zset[member] = score
                added += 1
        return added

    def _zscore(self, key: str, member: str) -> float | None:
        return self.zsets.get(key, {}).get(member)

    def _zrem(self, key: str, member: str) -> int:
        return 1 if self.zsets.get(key, {}).pop(member, None) is not None else 0

    def _zremrangebyscore(self, key: str, minimum: Any, maximum: Any) -> int:
        zset = self.zsets.get(key)
        if not zset:
            return 0
        low = None if str(minimum) == "-inf" else float(minimum)
        high = None if str(maximum) == "inf" else float(maximum)
        stale = [
            member
            for member, score in zset.items()
            if (low is None or score >= low) and (high is None or score <= high)
        ]
        for member in stale:
            zset.pop(member)
        return len(stale)

    class Pipeline:
        def __init__(self, store: FakeTokenStore) -> None:
            self._store = store
            self._ops: list[tuple[Any, ...]] = []

        async def __aenter__(self) -> FakeTokenStore.Pipeline:
            return self

        async def __aexit__(self, *exc_info: object) -> bool:
            return False

        def zadd(
            self, key: str, mapping: dict[str, float], gt: bool = False
        ) -> FakeTokenStore.Pipeline:
            self._ops.append(("zadd", key, mapping, gt))
            return self

        def expireat(self, key: str, when: Any) -> FakeTokenStore.Pipeline:
            del key, when
            self._ops.append(("expireat",))
            return self

        def zremrangebyscore(self, key: str, minimum: Any, maximum: Any) -> FakeTokenStore.Pipeline:
            self._ops.append(("zremrangebyscore", key, minimum, maximum))
            return self

        def zscore(self, key: str, member: str) -> FakeTokenStore.Pipeline:
            self._ops.append(("zscore", key, member))
            return self

        def zrem(self, key: str, member: str) -> FakeTokenStore.Pipeline:
            self._ops.append(("zrem", key, member))
            return self

        async def execute(self) -> list[Any]:
            results: list[Any] = []
            for op in self._ops:
                if op[0] == "zadd":
                    results.append(self._store._zadd(op[1], op[2], op[3]))
                elif op[0] == "expireat":
                    results.append(True)
                elif op[0] == "zremrangebyscore":
                    results.append(self._store._zremrangebyscore(op[1], op[2], op[3]))
                elif op[0] == "zscore":
                    results.append(self._store._zscore(op[1], op[2]))
                elif op[0] == "zrem":
                    results.append(self._store._zrem(op[1], op[2]))
            self._ops.clear()
            return results


@pytest_asyncio.fixture
async def auth_client(
    db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> AsyncIterator[tuple[AsyncClient, FakeTokenStore]]:
    store = FakeTokenStore()

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        yield db_session

    async def override_get_cache() -> FakeTokenStore:
        return store

    monkeypatch.setattr(limiter, "enabled", False)
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_async_cache] = override_get_cache
    try:
        # Secure cookies only travel over https requests in httpx's cookie jar.
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="https://test") as test_client:
            yield test_client, store
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_async_cache, None)


async def create_session_user(
    db_session: AsyncSession, email: str, password: str, *, is_active: bool = True
) -> User:
    user = await user_service.create_user(
        db_session,
        obj_in=UserCreate(email=email, password=password, full_name="Session Fixture"),
    )
    if not is_active:
        user.is_active = False
        await db_session.flush()
    return user


async def login(client: AsyncClient, email: str, password: str) -> Any:
    return await client.post(
        "/api/v0/authen/login",
        data={"username": email, "password": password},
    )


@pytest.mark.api
async def test_login_returns_token_pair_and_sets_protected_cookies(
    auth_client: tuple[AsyncClient, FakeTokenStore], db_session: AsyncSession
) -> None:
    client, store = auth_client
    await create_session_user(db_session, "owner@example.com", "correct-password")

    response = await login(client, "owner@example.com", "correct-password")

    assert response.status_code == 200
    body = response.json()
    # Login responds with the bare Token schema, not the shared success envelope.
    assert set(body) == {"access_token", "refresh_token", "token_type"}
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["refresh_token"]

    cookies = response.headers.get_list("set-cookie")
    for name in ("access_token", "refresh_token"):
        entry = next(header for header in cookies if header.startswith(f"{name}="))
        assert "httponly" in entry.lower()
        assert "secure" in entry.lower()
        assert "samesite=none" in entry.lower()
        assert "expires=" in entry.lower()
    # The refresh token is registered for server-side revocation.
    assert store.zsets["RefreshToken:owner@example.com"]


@pytest.mark.api
async def test_login_failures_do_not_set_cookies(
    auth_client: tuple[AsyncClient, FakeTokenStore], db_session: AsyncSession
) -> None:
    client, _ = auth_client
    await create_session_user(db_session, "owner@example.com", "correct-password")
    await create_session_user(
        db_session, "inactive@example.com", "inactive-password", is_active=False
    )

    wrong_password = await login(client, "owner@example.com", "wrong-password")
    assert wrong_password.status_code == 401
    assert wrong_password.json()["error"]["code"] == "unauthorized"

    unknown_email = await login(client, "missing@example.com", "any-password")
    assert unknown_email.status_code == 404
    assert unknown_email.json()["error"]["code"] == "not_found"

    inactive = await login(client, "inactive@example.com", "inactive-password")
    assert inactive.status_code == 403
    assert inactive.json()["error"]["code"] == "not_enough_privileges"

    for response in (wrong_password, unknown_email, inactive):
        assert not any(
            header.startswith(("access_token=", "refresh_token="))
            for header in response.headers.get_list("set-cookie")
        )


@pytest.mark.api
async def test_users_me_verifies_session_server_side(
    auth_client: tuple[AsyncClient, FakeTokenStore], db_session: AsyncSession
) -> None:
    client, _ = auth_client
    await create_session_user(db_session, "owner@example.com", "correct-password")

    anonymous = await client.get("/api/v0/users/me")
    assert anonymous.status_code == 401
    assert anonymous.json()["error"]["code"] == "unauthorized"

    await login(client, "owner@example.com", "correct-password")
    current = await client.get("/api/v0/users/me")
    assert current.status_code == 200
    body = current.json()
    assert body["status"] == "success"
    assert body["data"]["email"] == "owner@example.com"


@pytest.mark.api
async def test_refresh_rotates_single_use_refresh_token(
    auth_client: tuple[AsyncClient, FakeTokenStore], db_session: AsyncSession
) -> None:
    client, store = auth_client
    await create_session_user(db_session, "owner@example.com", "correct-password")
    # Seed a refresh token with a non-default expiry so rotation must mint a
    # distinct token (tokens minted in the same second are identical).
    old_expire = datetime.now(timezone.utc) + timedelta(hours=1)
    old_refresh = create_token(
        "owner@example.com",
        secret_key=settings.TOKEN.REFRESH_TOKEN_SECRET_KEY,
        expire=old_expire,
    )
    await refresh_token_repository.add(
        connection=cast(Any, store),
        email="owner@example.com",
        token=old_refresh,
        expire=old_expire,
    )

    # A request without a refresh cookie or header cannot rotate a session.
    client.cookies.clear()
    missing = await client.post("/api/v0/authen/refresh")
    assert missing.status_code == 401
    assert missing.json()["error"]["code"] == "unauthorized"

    refreshed = await client.post(
        "/api/v0/authen/refresh",
        cookies={"refresh_token": old_refresh},
    )
    assert refreshed.status_code == 200
    body = refreshed.json()
    # Refresh responds with the shared success envelope wrapping the Token schema.
    assert body["status"] == "success"
    assert set(body["data"]) == {"access_token", "refresh_token", "token_type"}
    assert body["data"]["refresh_token"] != old_refresh

    # Only the rotated refresh token remains valid; the old one is single-use.
    assert list(store.zsets["RefreshToken:owner@example.com"]) == [body["data"]["refresh_token"]]
    # Drop the rotated cookies the refresh response stored before replaying the
    # old token, so only the old token is sent.
    client.cookies.clear()
    reuse = await client.post(
        "/api/v0/authen/refresh",
        cookies={"refresh_token": old_refresh},
    )
    assert reuse.status_code == 401


@pytest.mark.api
async def test_logout_revokes_refresh_session_and_clears_cookies(
    auth_client: tuple[AsyncClient, FakeTokenStore], db_session: AsyncSession
) -> None:
    client, store = auth_client
    await create_session_user(db_session, "owner@example.com", "correct-password")
    login_response = await login(client, "owner@example.com", "correct-password")
    refresh_token = login_response.json()["refresh_token"]
    assert store.zsets["RefreshToken:owner@example.com"]

    response = await client.post("/api/v0/authen/logout")
    assert response.status_code == 204
    cookies = response.headers.get_list("set-cookie")
    for name in ("access_token", "refresh_token"):
        assert any(header.startswith(f"{name}=") for header in cookies)

    # The revoked refresh token cannot mint a new session.
    assert not store.zsets.get("RefreshToken:owner@example.com")
    reuse = await client.post(
        "/api/v0/authen/refresh",
        cookies={"refresh_token": refresh_token},
    )
    assert reuse.status_code == 401
