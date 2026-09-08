# Users — identity + profile store

Owns the `user` row: credentials (bcrypt hash only), profile/preferences, account status, 2FA flags, login timestamps. No finance logic lives here; `authen/` consumes `user_service` for login/refresh/token flows, and `User.items` is the owner anchor for user-owned resources (e.g. `Item.owner`).

Standard path: `router/v0.py` validates → `services.py` rules → `db_repository.py` SQL. See `api/AGENTS.md` for shared conventions (async, `Annotated` Depends, `SuccessfulResponse` envelope).

## File map — which file to read when

| Task                                             | Read first                   |
| ------------------------------------------------ | ---------------------------- |
| Change endpoint, param, response shape           | `router/v0.py`, `schemas.py` |
| Change creation/update/password/2FA/status rules | `services.py`                |
| Change SQL lookup (`email`, get-or-create)       | `db_repository.py`           |
| Change column/constraint/relation                | `db_models.py`               |
| Change request/response validation               | `schemas.py`                 |
| Change error code/shape                          | `errors.py`                  |
| Change first-admin seeding                       | `init_superuser.py`          |

`__init__.py` and `dependencies.py` are empty placeholders (no module exports, no custom dependencies — auth comes from `authen/dependencies.py`). `router/__init__.py` only mounts `v0.router` at `/v0/users` with tag `Users`.

## DB (`db_models.py`: table `user`)

Table name is auto-derived (`Base.__tablename__` → `user`). Inherits `TimestampMixin` (`created_at`, `updated_at`, tz-aware via `TZDateTime`).

| Column                | Type / constraint                | Notes                                                                                  |
| --------------------- | -------------------------------- | -------------------------------------------------------------------------------------- |
| `id`                  | int PK, indexed                  | Internal ID; exposed as number on the wire                                             |
| `email`               | str, `unique`, indexed, not null | Lookup key; case handling is exact-match (`WHERE email ==`)                            |
| `hashed_password`     | str, not null                    | bcrypt via `app.core.auth.security.get_password_hash`; never returned                  |
| `full_name`           | str \| null                      |                                                                                        |
| `avatar_url`          | str \| null                      |                                                                                        |
| `default_currency`    | `String(3)`, default `"VND"`     | e.g. `VND`                                                                             |
| `language_preference` | `String(5)`, default `"vi-VN"`   |                                                                                        |
| `is_active`           | bool, default `True`, nullable   | `get_current_active_user` rejects inactive                                             |
| `two_factor_enabled`  | bool, default `False`, not null  |                                                                                        |
| `two_factor_secret`   | str \| null                      | Set/cleared with the flag; no TOTP verification lives in this module                   |
| `registration_date`   | tz-aware, default `func.now()`   | Set explicitly in `UserService.create` with `datetime.now(tz.tzlocal())`               |
| `last_login_date`     | tz-aware, nullable               | Only written by `update_last_login`                                                    |
| `account_status`      | str, default `"ACTIVE"`          | Free string; router only accepts `ACTIVE`/`SUSPENDED`/`DELETED` on the status endpoint |

Relations: `items: list[Item]` ↔ `Item.owner` (`lazy="select"`). No cascade/delete-orphan configured here — check `items` module before deleting a user.

## Schemas (`schemas.py`)

All use `OptionalField` (nullable + omitted from JSON schema default). `UserInDBBase` has `from_attributes=True`.

- `UserBase` — shared optional fields: `email`, `is_active=True`, `full_name`, `avatar_url`, `default_currency="VND"`, `language_preference="vi-VN"`, `account_status="ACTIVE"`.
- `UserCreate(UserBase)` — requires `email: EmailStr` + `password: str` (plain, hashed in service).
- `UserCreateOpen(UserCreate)` — same shape, re-declares currency/language defaults; used by public registration.
- `UserLogin` — `email` + `password` (defined here, consumed conceptually by `authen/`).
- `UserUpdate(UserBase)` — all-optional incl. `password`; full admin update body.
- `UserUpdateMe` — self-service subset only: `password`, `full_name`, `avatar_url`, `default_currency`, `language_preference` (no `email`, no `account_status`, no `is_active`).
- `User` (response) = `UserInDBBase`: `id`, `email`, `registration_date`, `last_login_date`, `two_factor_enabled`, `two_factor_secret` + base fields. Note: `two_factor_secret` is currently serialized to the client — keep in mind when touching 2FA.
- `UserInDB` adds `hashed_password` (never used as a response model).

## Services (`services.py`) — key functions

Singleton `user_service = UserService(model=User, db_repository=user_db_repository)`. `authen/services.py` imports this instance.

- `create(db, obj_in: UserCreate)` — builds `User` with hashed password, `is_active=True`, `account_status="ACTIVE"`, explicit `registration_date`; delegates persist to repository. Use for programmatic/admin creation.
- `create_user(db, *, obj_in)` — wraps `create` + sends welcome email via `send_new_account_email` iff `settings.EMAIL.ENABLED`. Used by router + superuser seed.
- `get_or_create_by_email(db, email, **kwargs)` / `get_by_email(db, *, email)` / `get(db, id)` / `get_all` / `get_multi(offset, limit)` / `get_multi_count` — reads; `get_multi_count` = page + `count_all` for pagination.
- `update(db, db_obj, obj_in: UserUpdate | dict)` — `dict(exclude_unset=True)` for Pydantic input; passes raw dict straight through (no password hashing here — callers must hash first).
- `update_user_me(...)` — allow-listed self update; builds an empty `UserUpdate` and sets only non-`None` fields. Password must be handled separately via `update_password` (router does this).
- `update_password(db, db_obj, new_password)` — hashes then writes `hashed_password`.
- `update_last_login(db, db_obj)` — stamps `last_login_date = now(local)`.
- `update_account_status(db, db_obj, status)` — raw string write; validation (`ACTIVE/SUSPENDED/DELETED`) lives in the router, not here.
- `enable_two_factor(db, db_obj, secret)` / `disable_two_factor(db, db_obj)` — flip flag + set/clear secret.
- `delete(db, db_obj)` — hard delete; no usage check, no cascade — prefer status change (`DELETED`) unless you handle `items`.

## Repository (`db_repository.py`)

`UserDbRepository(BaseDbRepository[User])` inherits generic `create/get/get_multi/count_all/update/delete`. Module-specific:

- `get_by_email(db, *, email)` — `SELECT ... WHERE email == :email`, `one_or_none`.
- `get_or_create_by_email(db, email, **kwargs)` — select first; on miss `INSERT` + commit + refresh; on `IntegrityError` (race) rollback and re-select, returning `(user, False)`. Returns `(user, created: bool)`.

## Errors (`errors.py`)

Thin wrappers over `app.errors`: `user_not_found()` → 404 `"User not found"`; `exists_email(msg)`, `user_not_verified(msg)`, `user_already_verified(msg)` → 400 with `details.error_type` set (`exists_email`, `user_not_verified`, `user_already_verified`). Only `user_not_found` and `exists_email` are used by `router/v0.py` today.

## API (`router/v0.py`, prefix `/v0/users`)

All responses are `SuccessfulResponse[...]`. Auth: every route except `POST /open` requires `get_current_active_user` (`Db = get_db`, `CurrentUser` aliases). Pagination on list uses `fastapi-pagination` (`get_params` → `resolve_params` → `get_limit_offset` → `create_page`).

| Method + path                                | Auth                  | Service call                                              | Notes                                                                                                       |
| -------------------------------------------- | --------------------- | --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `GET /`                                      | yes                   | `get_multi_count`                                         | Paginated `Page[User]`                                                                                      |
| `POST /`                                     | yes (any active user) | `create_user`                                             | No duplicate-email check — relies on DB unique constraint; no admin-role gate in this module                |
| `POST /open`                                 | no                    | `get_by_email` → `create_user`                            | Gated by `settings.USER.OPEN_REGISTRATION` else `api_disabled`; duplicate email → `exists_email` (400)      |
| `GET /me`                                    | yes                   | — (returns `current_user`)                                | No DB round-trip                                                                                            |
| `PATCH /me`                                  | yes                   | `get(id)` → optional `update_password` → `update_user_me` | 404 if row vanished; `email`/`status` not self-editable                                                     |
| `POST /login-update`                         | yes                   | `update_last_login`                                       | Stamps `last_login_date` for caller (typically post-login)                                                  |
| `POST /two-factor/enable` (`secret` in body) | yes                   | `enable_two_factor`                                       | Stores raw secret; no OTP proof-of-possession here                                                          |
| `POST /two-factor/disable`                   | yes                   | `disable_two_factor`                                      | Clears secret                                                                                               |
| `GET /{user_id}`                             | yes                   | `get`                                                     | 404 if missing; `user == current_user` branch is a no-op (same response either way)                         |
| `PUT /{user_id}`                             | yes                   | `get` → `update`                                          | Full-model update incl. `password` field passed raw — hashing is NOT applied on this path, handle with care |
| `PUT /{user_id}/status` (`status` in body)   | yes                   | `get` → `update_account_status`                           | Strict allow-list; other values → 400 `HTTPException`                                                       |

## Main flows

**Admin/authenticated creation — `POST /`:** body `UserCreate` → `create_user` (hash + row + optional welcome email) → `User`. No pre-flight email check, so a duplicate surfaces as a DB integrity error, not `exists_email`.

**Public registration — `POST /open`:** requires `USER.OPEN_REGISTRATION=true` (default `false` in `app/configs/config.yml`) → `get_by_email` guard → `create_user`. Only entry point reachable without a token.

**Self update — `PATCH /me`:** re-fetch row by `current_user.id` (404 if deleted) → if `password` present, `update_password` first → `update_user_me` allow-list for the rest. Email/status changes must go through `PUT /{id}`.

**Login timestamp — `POST /login-update`:** caller (login flow in `authen/`) stamps `last_login_date` after successful auth.

**2FA toggle:** `enable` persists caller-supplied `secret` + flag; `disable` clears both. Verification logic lives outside this module.

**First-admin seed — `init_superuser(db) -> bool`:** called at startup/migrate; `get_by_email(FIRST_USER_EMAIL)` → if missing, `create_user(UserCreate(email, password, full_name))` from `settings.USER.FIRST_USER_*` and return `True`, else `False`. Imports `app.src.db_models` for Alembic model discovery side effect.

## Consumed by / coupling

- `authen/` depends on `user_service` (lookup by email, `update_password`, token-subject → user) and on the `User` ORM row for `get_current_user`/`get_current_active_user`. Changing `email` semantics, `is_active`, or `hashed_password` breaks auth.
- `app/src/route.py` includes `users_router`; ORM model must stay importable via `app/src/db_models.py` for Alembic.
- `settings.USER` (`OPEN_REGISTRATION`, `FIRST_USER_EMAIL/PASSWORD/FULL_NAME`) in `app/configs/config.yml` + env controls `/open` and seeding.

## Conventions when editing

- Keep the layering: validation in router/schemas, hashing + field allow-lists in `services.py`, SQL in `db_repository.py`. Never write `hashed_password` from the router.
- `UserUpdate` carries a plain `password` field but `update()` does not hash — either route it through `update_password` or add explicit hashing; do not expose `PUT /{id}` password writes as-is without checking.
- Email lookup is exact-match; adding case-insensitivity means changing both `get_by_email` and `get_or_create_by_email` (plus a migration if you want a functional unique index).
- Status strings are router-validated only; `update_account_status` trusts its caller — keep new statuses in sync in both places.
- `User` response currently leaks `two_factor_secret`; do not add more secrets to response schemas, and consider excluding it when touching 2FA.
- `is_active=False` locks the user out globally via `get_current_active_user`; `account_status` is informational unless a caller checks it — don't confuse the two.
