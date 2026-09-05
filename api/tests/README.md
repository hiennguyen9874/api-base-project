# API tests

Tests are split by scope:

- `unit/`: no database, HTTP server, or other external service.
- `integration/`: repository/service tests against PostgreSQL.
- `api/`: requests made in-process through HTTPX and FastAPI.
- `factories/`: reusable fixture factories.

PostgreSQL-backed tests use a transaction per test. Application `commit()` calls are
contained in a savepoint and teardown rolls back the outer transaction.

From the repository root:

```bash
make test-api-db-up
make test-api
make test-api-db-down
```

For tests that do not need PostgreSQL:

```bash
make test-api-unit
```

Set `TEST_DATABASE_URL` to override the default test DSN
(`postgresql+asyncpg://test:test@localhost:5433/cashlens_test`). The ASGI fixtures do
not run application lifespan because normal startup requires Redis and RabbitMQ; add a
focused lifespan fixture when those integrations are under test.
