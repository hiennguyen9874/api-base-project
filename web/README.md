# CashLens web

React and Vite frontend for CashLens.

## Integrated development stack

From the repository root, copy the local example once and start the complete
API and frontend stack:

```bash
cp .env.example .env
make up
```

Open `http://localhost:5173`. The browser uses same-origin `/api` requests and
Vite proxies them to the API container. Set `VITE_ENABLE_MSW=true` in the root
`.env` only when intentionally using sanitized MSW handlers.

Optional database/cache tools are available on loopback-only ports:

```bash
make up-tools
```

## Production stack

The production stack is started from the repository root after creating
`.env.production` from `.env.production.example`:

```bash
cp .env.production.example .env.production
# Replace every CHANGE_ME value, then:
make up-prod
```

It serves the SPA and `/api` through one reverse-proxy origin.
Release images therefore use an empty `VITE_API_BASE_URL` and are reusable
across environments.

## Local package commands

Use pnpm from this directory:

```bash
pnpm install --frozen-lockfile
pnpm build
pnpm lint
pnpm format:check
pnpm test
pnpm test:e2e
```

Generate the API client only from the supported Compose API:

```bash
CASHLENS_OPENAPI_URL=http://localhost:11112/openapi.json pnpm api:generate
```

## Authentication deployment gate

Production should use HTTPS and the integrated same-origin topology. Verify in
Chromium that login, reload, refresh rotation, and logout preserve the Secure,
HttpOnly cookies. If a cross-origin deployment is unavoidable, configure the
exact frontend CORS origin and validate `SameSite=None`; never move tokens into
browser storage.
