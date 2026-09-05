# CashLens

CashLens is a monorepo for a private finance dashboard and its FastAPI backend. The intended product is a **read-only, one-way Money Lover mirror**: provider access, synchronization, authorization, and aggregation belong on the server; the browser consumes owner-authorized CashLens APIs.

## Workspace map

- `api/` — async FastAPI, PostgreSQL/PgBouncer, Redis, RabbitMQ, and Taskiq workers. **For any API, database, migration, authentication, or task work, read `api/AGENTS.md`.**
- `web/` — React + TypeScript Vite SPA. **For frontend, generated-client, test, or UI work, read `web/AGENTS.md`.**
- `docs/database-design.md` — proposed Money Lover schema and reporting semantics. **Read it before changing financial models, synchronization, reports, frontend financial views, API mocks, or connection state.** It is not proof that endpoints or migrations exist.
- `docker-compose.dev.yml` — local backend stack; `Makefile` — root Compose and Alembic commands.

## Cross-cutting rules

- Treat the implemented FastAPI OpenAPI document as the frontend API contract. Regenerate `web/src/api/generated/` with Orval rather than editing generated files or inventing endpoints to satisfy UI work.
- Preserve financial correctness across boundaries: backend `Decimal`/PostgreSQL numeric values and bigint identifiers must not be silently coerced to JavaScript numbers; group totals by currency and keep business arithmetic server-side.
- Keep Money Lover credentials, raw provider payloads, and private sample data server-side. Use sanitized, contract-backed fixtures for browser mocks and tests.
- Keep each package’s lockfile with its manifest. Start the local backend stack from the repository root with `make up`; run frontend package commands from `web/` with pnpm.
