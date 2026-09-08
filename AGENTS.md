# CashLens

CashLens is a monorepo for a private finance dashboard and its FastAPI backend. The intended product is a **read-only, one-way Money Lover mirror**: provider access, synchronization, authorization, and aggregation belong on the server; the browser consumes owner-authorized CashLens APIs.

## Workspace map

- `api/` — async FastAPI, PostgreSQL/PgBouncer, Redis, RabbitMQ, and Taskiq workers. **For any API, database, migration, authentication, or task work, read `api/AGENTS.md`.**
- `web/` — React + TypeScript Vite SPA. **For frontend, generated-client, test, or UI work, read `web/AGENTS.md`.**
- `compose.yaml` plus `compose.dev.yaml` / `compose.prod.yaml` — shared, development, and production stacks; `Makefile` — root Compose and Alembic commands.

## Cross-cutting rules

- Treat the implemented FastAPI OpenAPI document as the frontend API contract. Regenerate `web/src/api/generated/` with Orval rather than editing generated files or inventing endpoints to satisfy UI work.
- Preserve financial correctness across boundaries: backend `Decimal`/PostgreSQL numeric values and bigint identifiers must not be silently coerced to JavaScript numbers; group totals by currency and keep business arithmetic server-side.
- Keep Money Lover credentials, raw provider payloads, and private sample data server-side. Use sanitized, contract-backed fixtures for browser mocks and tests.
- Keep each package’s lockfile with its manifest. Start the local backend stack from the repository root with `make up`; run frontend package commands from `web/` with pnpm.

### Generated API client

When a FastAPI contract changes, generate the client against the supported Compose API rather than a host `uvicorn` process. Start the stack with `make up`, wait for `http://localhost:<APP__API_PORT>/openapi.json` to respond, then run `cd web && CASHLENS_OPENAPI_URL=http://localhost:<APP__API_PORT>/openapi.json pnpm api:generate`. Use the value from the active root `.env`; `.env.example` maps the API to port `11112`. `CASHLENS_OPENAPI_URL` defaults to `http://localhost:8000/openapi.json` for existing local setups. Do not use host-only settings or logging overrides to serve OpenAPI.

## Agent skills

### Issue tracker

Issues are tracked in this repository’s GitHub Issues via `gh`. See `docs/agents/issue-tracker.md`.

### Triage labels

The default five canonical triage labels are used. See `docs/agents/triage-labels.md`.

### Domain docs

This repository uses a multi-context domain-doc layout. See `docs/agents/domain.md`.
