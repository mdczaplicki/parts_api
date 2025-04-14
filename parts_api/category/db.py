from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncConnection

from parts_api.category.table import CategoryTable
from parts_api.db import inject_db_connection


@inject_db_connection
async def insert_many_categories(
    db_connection: AsyncConnection, names: list[str]
) -> None:
    statement = insert(CategoryTable).values(
        [{CategoryTable.name: name} for name in names]
    )
    await db_connection.execute(statement)
