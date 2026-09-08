# syntax=docker/dockerfile:1

# ------------------------------------------------------------
# Base
# ------------------------------------------------------------
FROM node:22-bookworm-slim AS base

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

WORKDIR /app

RUN corepack enable


# ------------------------------------------------------------
# Dependencies
# Shared by development and production build.
# ------------------------------------------------------------
FROM base AS deps

# Keep dependency manifests separate from source code for better cache reuse.
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

RUN --mount=type=cache,id=cashlens-pnpm-store,target=/pnpm/store \
    pnpm install --frozen-lockfile


# ------------------------------------------------------------
# Development
# docker build --target development
# ------------------------------------------------------------
FROM deps AS development

ENV NODE_ENV=development

COPY . .

EXPOSE 5173

CMD ["pnpm", "dev", "--host", "0.0.0.0", "--port", "5173"]


# ------------------------------------------------------------
# Production build
# ------------------------------------------------------------
FROM deps AS build

COPY . .

# Vite replaces these values at build time. MSW is disabled by default so it
# cannot accidentally be included as the production bootstrap.
ARG VITE_API_BASE_URL=""
ARG VITE_ENABLE_MSW=false
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV VITE_ENABLE_MSW=${VITE_ENABLE_MSW}

RUN pnpm build


# ------------------------------------------------------------
# Production runtime
# Node / pnpm / source files / dev dependencies are intentionally
# absent from the final image.
# ------------------------------------------------------------
FROM nginxinc/nginx-unprivileged:1.30.4-alpine-slim AS production

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 8080
