from uuid import UUID

from sqlalchemy import insert, delete, select
from sqlalchemy.ext.asyncio import AsyncConnection

from parts_api.db import inject_db_connection
from parts_api.manufacturer.schema import Manufacturer
from parts_api.manufacturer.table import ManufacturerTable


@inject_db_connection
async def clear_manufacturers(db_connection: AsyncConnection) -> None:
    statement = delete(ManufacturerTable)
    await db_connection.execute(statement)


@inject_db_connection
async def insert_many_manufacturers(
    names: list[str], db_connection: AsyncConnection
) -> dict[str, UUID]:
    statement = (
        insert(ManufacturerTable)
        .values([{ManufacturerTable.name: name} for name in names])
        .returning(ManufacturerTable.uuid, ManufacturerTable.name)
    )
    result = await db_connection.execute(statement)
    return {row.name: row.uuid for row in result}


@inject_db_connection
async def select_manufacturers(
    name: str | None, uuid: UUID | None, db_connection: AsyncConnection
) -> list[Manufacturer]:
    statement = select(ManufacturerTable.name, ManufacturerTable.uuid)
    if name is not None:
        statement = statement.where(ManufacturerTable.name == name)
    if uuid is not None:
        statement = statement.where(ManufacturerTable.uuid == uuid)
    result = await db_connection.execute(statement)
    return [Manufacturer.model_validate(row, from_attributes=True) for row in result]
