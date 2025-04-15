format:
	uv run ruff check --fix .
	uv run ruff format .

check:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy .

test:
	DATABASE_CONNECTION_STRING="postgresql+asyncpg://parts:parts@localhost:5432/parts-db" uv run pytest .

build:
	docker compose build base_app

migrate:
	docker compose up migrate

scrape:
	docker compose up -d scraper

up:
	docker compose up -d api

down:
	docker compose down