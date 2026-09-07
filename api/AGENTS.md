# API instructions

## Scope

This directory contains the async FastAPI service. Run API commands from the repository root unless a command says otherwise. Python is locked to 3.10; use `uv` and keep `uv.lock` in sync with dependency changes.

## Architecture

- `app/main.py` creates the application and exposes `/health`; `app/core/app_factory.py` configures lifespan, middleware, exception handling, Swagger, static files, Taskiq, and the `/api` router.
- `app/src/route.py` aggregates versioned feature routers. Features live under `app/src/<feature>/` (`router/`, `schemas.py`, `services.py`, `db_repository.py`, `db_models.py`, and feature errors as needed).
- Keep the request path explicit: router → service → database/cache repository. Routers validate and assemble responses; services own business rules; repositories own SQLAlchemy/Redis access.
- Use the `get_db` and `get_async_cache` dependencies from `app/src/dependencies.py`; type dependencies with `Annotated[..., Depends(...)]`. Preserve async I/O through the stack.
- Use shared response schemas in `app/schemas/` and raise centralized `app.errors` / feature error helpers so registered handlers produce the standard envelope.
- Add a feature router to `app/src/route.py`. Import ORM models through `app/src/db_models.py` so Alembic discovers metadata.

## Data, auth, and tasks

- SQLAlchemy uses async sessions and PostgreSQL via PgBouncer. Review generated migrations in `app/alembic/versions/`; the prestart service applies migrations and seeds initial data.
- Authentication supports Bearer tokens and cookies. Refresh-token revocation is stored in Redis (`app/core/auth/refresh_token_repository.py`); preserve it when changing login, refresh, or logout flows.
- Define Taskiq tasks with the broker in `app/core/messaging/taskiq_broker.py`. `app/worker.py` imports task modules and owns worker lifecycle; Compose runs `taskiq worker app.worker:broker app.src.tasks` and its scheduler counterpart.
- Settings combine `__`-nested environment variables with `app/configs/config.yml`. The configured YAML path is `/app/app/configs/config.yml`, so container execution is the supported default. Use `.env.example` as the variable reference; never add secrets to configuration or logs.

## Tests

- Tests live in `tests/`: use `unit/` for tests without external services, `integration/` for PostgreSQL-backed repository/service tests, `api/` for HTTP tests, and `factories/` for reusable fixture factories.
- PostgreSQL tests use `compose.test.yaml` and default to `postgresql+asyncpg://test:test@localhost:5433/cashlens_test`. Override this with `TEST_DATABASE_URL` when needed.
- Database tests create the metadata schema once and run each test in an outer transaction. Keep `AsyncSession(..., join_transaction_mode="create_savepoint")` so application commits remain rollback-safe.
- Async API tests use HTTPX `AsyncClient` with `ASGITransport`. The default clients do not run application lifespan because normal startup requires Redis and RabbitMQ; add a focused lifespan fixture when testing those integrations.
- Mark tests with `unit`, `integration`, and/or `api`. Add targeted tests with behavior changes. See `tests/README.md` for details.
- After an edit, run only the tests covering it and cap harness output, e.g. `cd api && uv run pytest tests/unit/test_foo.py -q --tb=short 2>&1 | tail -n 30`; a single DB-backed error already prints ~100 lines, and the full suite without PostgreSQL emits ~15k lines of repeated connection tracebacks. Start the test database (`make test-api-db-up`) before `make test-api` / `make test-api-db`, and tail those full runs the same way.

## Commands and checks

```bash
# repository root
make up
make down
make migrate
make migration msg="describe schema change"
make test-api-db-up
make test-api
make test-api-db-down
make test-api-unit
make lint
make lint-ruff [FILES=api/app/src/foo.py]
make lint-format [FILES=api/app/src/foo.py]
make lint-mypy [FILES=api/app/src/foo.py]
make lint-bandit [FILES=api/app/src/foo.py]
make lint-isort lint-autoflake
```

`make up` runs the `prestart` service, which migrates, checks connections, and creates initial data. `make test-api` expects the test PostgreSQL container for integration tests; `make test-api-unit` does not. Run linters from the repository root via `make lint` (full pre-commit) or `make lint-<ruff|format|mypy|bandit|isort|autoflake>` for a single pre-commit hook with the same config. After an edit, check only the files touched and cap harness output, e.g. `make lint-ruff FILES=api/app/src/foo.py 2>&1 | tail -n 40`; reserve full `make lint` for the final gate and tail it the same way, since its `--all-files --show-diff-on-failure --color=always` flags dump the whole-repo diff and ANSI codes into the log. Prefer these over bare `cd api && uv run <ruff|mypy|bandit|black>`, which drift from pre-commit config (missing binary/args) and `black` conflicts with the canonical `ruff-format`; Alembic is excluded, so inspect migration revisions manually.

## Conventions

- Match existing four-space Python, full annotations, 100-column formatting, and Python 3.10 compatibility. Mypy disallows untyped function definitions.
- Scope every persisted resource to the authenticated owner before reading or mutating it; do not let a convenient repository lookup bypass authorization.
