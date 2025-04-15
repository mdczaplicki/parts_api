from contextlib import asynccontextmanager
from typing import AsyncGenerator

import pytest
from pytest_mock import MockFixture
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncConnection

from build.lib.parts_api.settings.db import DATABASE_SETTINGS
from parts_api import db


@pytest.fixture()
async def db_engine_for_tests() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(DATABASE_SETTINGS.connection_string)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture()
async def async_connection(  # type: ignore[misc]
    db_engine_for_tests: AsyncEngine,
    mocker: MockFixture,
) -> AsyncConnection:
    async with db_engine_for_tests.connect() as connection:

        @asynccontextmanager
        async def mocked_connection():
            yield connection

        mocker.patch.object(db, db.db_connection.__name__, mocked_connection)
        yield connection
