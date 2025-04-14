from typing import Iterable
from uuid import UUID

from sqlalchemy import insert, delete
from sqlalchemy.ext.asyncio import AsyncConnection

from parts_api.category.table import CategoryTable
from parts_api.db import inject_db_connection


@inject_db_connection
async def clear_categories(db_connection: AsyncConnection) -> None:
    statement = delete(CategoryTable)
    await db_connection.execute(statement)


@inject_db_connection
async def insert_many_categories(
    names: Iterable[str], db_connection: AsyncConnection
) -> dict[str, UUID]:
    statement = (
        insert(CategoryTable)
        .values([{CategoryTable.name: name} for name in names])
        .returning(CategoryTable.uuid, CategoryTable.name)
    )
    result = await db_connection.execute(statement)
    return {row.name: row.uuid for row in result}
