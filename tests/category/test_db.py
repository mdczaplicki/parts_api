from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncConnection

from build.lib.parts_api.category import db
from parts_api.category.table import CategoryTable


async def test_insert_many_categories(async_connection: AsyncConnection) -> None:
    # given
    names = ["Hobbits", "Orcs"]

    # when
    await db.insert_many_categories(names, async_connection)

    # then
    statement = select(CategoryTable)
    result = await async_connection.execute(statement)
    assert len(list(result)) == len(names)
    assert set(row.name for row in result) == set(names)
