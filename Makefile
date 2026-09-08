DEV_ENV ?= .env
PROD_ENV ?= .env.production
COMPOSE_DEV := docker compose --env-file $(DEV_ENV) -f compose.yaml -f compose.dev.yaml
COMPOSE_PROD := docker compose --env-file $(PROD_ENV) -f compose.yaml -f compose.prod.yaml

.PHONY: migration migrate up down up-tools build-prod up-prod down-prod config-dev config-prod lint lint-ruff lint-format lint-mypy lint-bandit lint-isort lint-autoflake test-api-db-up test-api-db-down test-api test-api-unit test-api-db test-api-phase3

migration:
	@echo "Running Alembic migration with message: '$(msg)'"
	@$(COMPOSE_DEV) build prestart
	@$(COMPOSE_DEV) run --rm prestart alembic revision --autogenerate -m "$(msg)"

migrate:
	@echo "Running Alembic migrate"
	@$(COMPOSE_DEV) build prestart
	@$(COMPOSE_DEV) run --rm prestart alembic upgrade head

up:
	@$(COMPOSE_DEV) up -d --build

down:
	@$(COMPOSE_DEV) down

up-tools:
	@$(COMPOSE_DEV) --profile tools up -d

build-prod:
	@$(COMPOSE_PROD) build

up-prod:
	@$(COMPOSE_PROD) up -d

down-prod:
	@$(COMPOSE_PROD) down

config-dev:
	@$(COMPOSE_DEV) config --quiet

config-prod:
	@$(COMPOSE_PROD) config --quiet

lint:
	@uv run --project api pre-commit run --all-files --show-diff-on-failure --color=always

lint-ruff:
	@uv run --project api pre-commit run ruff $(if $(FILES),--files $(FILES),--all-files)

lint-format:
	@uv run --project api pre-commit run ruff-format $(if $(FILES),--files $(FILES),--all-files)

lint-mypy:
	@uv run --project api pre-commit run mypy $(if $(FILES),--files $(FILES),--all-files)

lint-bandit:
	@uv run --project api pre-commit run bandit $(if $(FILES),--files $(FILES),--all-files)

lint-isort:
	@uv run --project api pre-commit run isort $(if $(FILES),--files $(FILES),--all-files)

lint-autoflake:
	@uv run --project api pre-commit run autoflake $(if $(FILES),--files $(FILES),--all-files)

test-api-db-up:
	@docker compose -f api/compose.test.yaml up -d --wait

test-api-db-down:
	@docker compose -f api/compose.test.yaml down

test-api:
	@cd api && uv run pytest -q --tb=short

test-api-unit:
	@cd api && uv run pytest -q --tb=short -m unit

test-api-db:
	@cd api && uv run pytest -q --tb=short -m "integration or api"
