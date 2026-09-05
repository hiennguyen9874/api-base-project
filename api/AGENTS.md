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

## Commands and checks

```bash
# repository root
make up
make down
make migrate
make migration msg="describe schema change"
pre-commit run --all-files --show-diff-on-failure --color=always
```

`make up` runs the `prestart` service, which migrates, checks connections, and creates initial data. The configured pre-commit checks format/import cleanup, Ruff, mypy, and Bandit; Alembic is excluded, so inspect migration revisions manually. There is no checked-in API test suite or focused test command—add targeted tests with behavior changes, then run the relevant quality checks.

## Conventions

- Match existing four-space Python, full annotations, 100-column formatting, and Python 3.10 compatibility. Mypy disallows untyped function definitions.
- Scope every persisted resource to the authenticated owner before reading or mutating it; do not let a convenient repository lookup bypass authorization.
- The planned Money Lover domain is defined in `../docs/database-design.md`, not implemented API behavior. Read it before adding financial models, migrations, synchronization, or reporting; preserve `Decimal` precision and keep provider credentials/raw payloads server-side.
