.PHONY: migration migrate up down

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
