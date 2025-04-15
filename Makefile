format:
	uv run ruff check --fix .
	uv run ruff format .

check:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy .