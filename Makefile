.PHONY: migration migrate up down lint lint-ruff lint-format lint-mypy lint-bandit lint-isort lint-autoflake test-api-db-up test-api-db-down test-api test-api-unit test-api-db

migration:
	@echo "Running Alembic migration with message: '$(msg)'"
	@docker-compose -f docker-compose.dev.yml build prestart
	@docker-compose -f docker-compose.dev.yml run --rm prestart alembic revision --autogenerate -m "$(msg)"

migrate:
	@echo "Running Alembic migrate"
	@docker-compose -f docker-compose.dev.yml build prestart
	@docker-compose -f docker-compose.dev.yml run --rm prestart alembic upgrade head

up:
	@docker-compose -f docker-compose.dev.yml up -d

down:
	@docker-compose -f docker-compose.dev.yml down

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
	@cd api && uv run pytest

test-api-unit:
	@cd api && uv run pytest -m unit

test-api-db:
	@cd api && uv run pytest -m "integration or api"
