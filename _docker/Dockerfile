FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

ENV APP_DIR /opt/parts_api
WORKDIR ${APP_DIR}

COPY ./pyproject.toml ./uv.lock ./

RUN uv sync --frozen

COPY _migrations ./_migrations
COPY alembic.ini ./
COPY parts_api ./parts_api

RUN uv pip install .