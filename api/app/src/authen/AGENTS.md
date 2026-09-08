# authen — Authentication module

Owner of email/password login, JWT access/refresh issuance, refresh-token rotation and revocation, password recovery/reset, and the request guards other features depend on. Mounted at `/api/v0/authen` (router prefix `/v0/authen` + `API_PREFIX=/api`; see `app/src/route.py`, `app/core/app_factory.py`).

It owns **no Postgres table**. Identity lives in the `users` table (`app/src/users/db_models.py` → `User`); live refresh sessions live in Redis. Token crypto lives in `app/core/auth/security.py`; do not reimplement it here.

## File map

| File                          | Role — read it when…                                                                                                  |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `router/v0.py`                | HTTP surface. Read to change endpoints, cookies, rate limits, request/response shape.                                 |
| `router/__init__.py`          | Mounts `v0.router` at prefix `/v0/authen`, tag `Authentication`.                                                      |
| `services.py`                 | Business rules (`AuthenService` + singleton `authen_service`). Read to change login/refresh/logout/reset logic.       |
| `dependencies.py`             | Request guards (`get_current_*`, `get_refresh_token`, `OAuth2PasswordBearerWithCookie`). Read to protect a new route. |
| `refresh_token_repository.py` | Redis revocation store (`RefreshTokenRepository` + singleton). Read to change session storage.                        |
| `schemas.py`                  | `Token`, `TokenPayload`, `OIDCUser`.                                                                                  |
| `errors.py`                   | Error helpers mapping to `app.errors.AppException`.                                                                   |
| `__init__.py`                 | Empty.                                                                                                                |

Cross-module inputs this code assumes: `app/src/users/services.py` (`user_service.get_by_email/update_password`), `app/src/dependencies.py` (`get_db`, `get_async_cache`), `app/core/settings/token.py|email.py|ratelimit.py` + `PROTECT_MEDIA` in `app/core/settings/app.py`, `app/core/messaging/emails.py` (reset token + mailer). Note: root `api/AGENTS.md` cites a refresh-token repository under `app/core/auth/` — the actual implementation is this module's `refresh_token_repository.py`.

## Token and credential model

- JWTs are HS256 (`settings.TOKEN.ALGORITHM`), payload `{sub: <email>, exp: …}`. Access and refresh tokens use **separate secrets** (`ACCESS_TOKEN_SECRET_KEY` vs `REFRESH_TOKEN_SECRET_KEY`). Lifetimes: access `ACCESS_TOKEN_EXPIRE_DURATION` (default 11520 min = 8 days), refresh `REFRESH_TOKEN_EXPIRE_DURATION` (default 21600 min = 15 days).
- Password hashing/verify: `get_password_hash` / `verify_password` in `app/core/auth/security.py` (passlib bcrypt wrapper + raw bcrypt). Gotcha: `verify_password` discards the `pwd_context.verify()` return value when `using_bcrypt=False` and falls through to `bcrypt.checkpw` — login therefore effectively validates via `bcrypt.checkpw` against hashes produced by `pwd_context.hash` (bcrypt-compatible). Preserve this pairing when touching password code.
- Password-reset tokens are a **third JWT family** (`app/core/messaging/emails.py`: `generate_password_reset_token` / `verify_password_reset_token`), signed with `EMAIL.RESET_TOKEN_SECRET_KEY`, 60 min expiry. They never touch Redis.

## Storage

- Postgres `users` row (via `UserService`): lookup key is `email` (`sub` claim). Relevant columns: `email` (unique), `hashed_password`, `is_active`. `login()` and `reset_password()` reject `is_active=False` with `inactive_user` (FORBIDDEN); unknown email raises `users` `user_not_found`; bad password raises `wrong_password`.
- Redis refresh sessions: key `RefreshToken:{email}`, a **sorted set** where member = refresh-token string, score = expiry timestamp. `add()` uses `ZADD … GT`, `EXPIREAT`, plus lazy `ZREMRANGEBYSCORE -inf … now-1min` cleanup; `check()` runs the same cleanup then `ZSCORE`; `delete()` = `ZREM` + cleanup; `delete_all()` = `DEL` key. Every `check`/`add`/`delete` prunes expired entries, so stale members disappear without a sweeper.

## Flows

- **Login** — `POST /login` → `AuthenService.login(db, cache, email, password)`: `get_by_email` → `verify_password` → `is_active` check → `create_token()` mints both JWTs → `refresh_token_repository.add()` stores refresh in Redis → router sets `access_token` + `refresh_token` HttpOnly cookies (flags/expiry from `TOKEN.COOKIE_*`) and returns `Token{access_token, refresh_token, token_type:"bearer"}`. Form field `username` carries the email (`OAuth2PasswordRequestForm`). Rate-limited by `RATELIMIT.LOGIN_RATELIMIT1/2`.
- **Authenticated request** — `OAuth2PasswordBearerWithCookie.__call__` reads the `access_token` **cookie first**, else `Authorization: Bearer`. Guards: `get_current_user` (token → `get_user_from_token` → `get_by_email`; raises `not_authenticated` / app-level not-found) and `get_current_active_user` (adds `is_active` check). This last one is what `items`, `users` routers depend on — use it for new protected routes.
- **Refresh rotation** — `POST /refresh` with refresh token from cookie **or** `refresh_token` header (`get_refresh_token` dependency; raises `refresh_token_not_found` if neither): `parse_token(refresh secret)` → `check()` in Redis (miss → `refresh_token_not_found`) → `delete(old)` → re-lookup user → `create_token()` + `add(new)` → fresh cookies + new pair in body. Old token is single-use; concurrent reuse fails closed.
- **Logout / logout-all** — `POST /logout` (`logout()`: parse refresh token, `delete` that member) and `POST /logout-all` (`logout_all_with_token()`: parse then `delete_all` for the `sub` email). Both 204 and clear both cookies. `logout_all(email)` variant exists for server-side use (takes email directly).
- **Password recovery/reset** — `POST /password-recovery/{email}`: `recover_password` looks up user (unknown → generic not-found, no mail) then `generate_password_reset_token(email)` + `send_reset_password_email(...)` (link built from `EMAIL.SERVER_HOST`, validity text from `RESET_TOKEN_EXPIRE_HOURS`). `POST /reset-password` (`{token, new_password}` in body): `verify_password_reset_token` (None → `invalid_reset_password_token`) → user lookup + `is_active` check → `user_service.update_password`.
- **OIDC exchange** — `exchange_oidc_token(cache, user)` mints + stores a pair for an already-validated `User`. No OIDC validation happens here and no v0 route currently calls it; `schemas.OIDCUser` (active fields: `sub`, `email`, optional `name`/`username`/`preferred_username`/`email_verified`) is likewise unused by the router — check callers before assuming an OIDC login endpoint.
- **Media/static probe** — `GET /auth-static` with `get_current_media_user`: returns `None` (anonymous allowed) when `APP.PROTECT_MEDIA=False`; otherwise requires a valid access token. Handler body is `pass` — it exists for `auth_request`-style gating, not data.

## API (all under `/api/v0/authen`)

| Method + path                     | Auth input                                 | Success                                             |
| --------------------------------- | ------------------------------------------ | --------------------------------------------------- |
| `POST /login`                     | OAuth2 form (`username`=email, `password`) | 200 `Token`, sets both cookies                      |
| `POST /refresh`                   | `refresh_token` cookie or header           | 200 `{data: Token}` envelope, rotates cookies       |
| `POST /logout`                    | `refresh_token` cookie or header           | 204, clears cookies                                 |
| `POST /logout-all`                | `refresh_token` cookie or header           | 204, revokes all sessions for `sub`, clears cookies |
| `POST /password-recovery/{email}` | path email                                 | 200 `{msg}`                                         |
| `POST /reset-password`            | JSON body `{token, new_password}`          | 200 `{msg}`                                         |
| `GET /auth-static`                | optional access token (see above)          | 200 empty (gate only)                               |

## Key functions (search targets, not full-file reads)

- `services.py` — `AuthenService.login`, `.refresh_token` (rotation), `.create_token` (mint pair + expiries), `.parse_token` (decode + map `ExpiredSignatureError`→`expired_jwt_token`, `InvalidTokenError|ValidationError`→`invalid_jwt_token`), `.get_user_from_token` (access-secret decode → `get_by_email`), `.logout` / `.logout_all` / `.logout_all_with_token`, `.recover_password` / `.reset_password`, `.exchange_oidc_token`.
- `dependencies.py` — `OAuth2PasswordBearerWithCookie.__call__` (cookie-first extraction, `token_url=/api/v0/authen/login`), `get_current_active_user` (default guard), `get_current_media_user` (`PROTECT_MEDIA` branch), `get_refresh_token` (cookie-then-header).
- `refresh_token_repository.py` — `_key(email)`, `.check` (cleanup + `ZSCORE` presence test), `.add` (upsert-if-greater + `EXPIREAT` + prune), `.delete`, `.delete_all`.
- `errors.py` — `not_authenticated`, `invalid/expired_jwt_token`, `invalid_jwt_claims`, `token_not_found`, `refresh_token_not_set/not_found`, `invalid_reset_password_token`, `wrong_password` (all UNAUTHORIZED); `inactive_user` (FORBIDDEN).

## Settings knobs

`TOKEN.*` (algorithm, both secrets/expiries, `COOKIE_HTTPONLY/SECURE/SAMESITE`), `EMAIL.RESET_TOKEN_*` + `EMAIL.SERVER_HOST/ENABLED`, `RATELIMIT.LOGIN_*`, `APP.PROTECT_MEDIA`, `APP.API_PREFIX`. Secrets/expiries change token validity immediately for newly minted tokens; already-issued tokens keep old claims.

## Where to change what

- New protected endpoint → `Depends(get_current_active_user)` from `app.src.authen.dependencies`; scope rows to `current_user` (repo convention).
- Login/refresh/logout semantics → `services.py` + cookies in `router/v0.py`; session persistence → `refresh_token_repository.py`.
- Token lifetime/secret/cookie flags → `app/core/settings/token.py` (+ env), never hardcode in this module.
- User fields/lookup → `app/src/users/` (`db_models.py`, `services.py`); this module only calls `get_by_email` / `update_password`.
- Error shape → `errors.py` + global handlers (`app.errors`); keep UNAUTHORIZED vs FORBIDDEN split for `inactive_user`.
