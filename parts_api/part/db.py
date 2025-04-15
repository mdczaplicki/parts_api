from uuid import UUID

from sqlalchemy import insert, delete, select
from sqlalchemy.ext.asyncio import AsyncConnection

from parts_api.db import inject_db_connection
from parts_api.part.schema import CreatePartTuple, Part
from parts_api.part.table import PartTable


@inject_db_connection
async def clear_parts(db_connection: AsyncConnection) -> None:
    statement = delete(PartTable)
    await db_connection.execute(statement)


@inject_db_connection
async def insert_many_parts(
    create_schemas: list[CreatePartTuple], db_connection: AsyncConnection
) -> None:
    statement = insert(PartTable).returning(PartTable.uuid, PartTable.name)
    await db_connection.execute(
        statement,
        [
            {
                "name": s.name,
                "model_uuid": s.model_uuid,
            }
            for s in create_schemas
        ],
    )


@inject_db_connection
async def select_parts(
    name: str | None,
    uuid: UUID | None,
    model_uuid: UUID | None,
    page: int,
    page_size: int,
    db_connection: AsyncConnection,
) -> list[Part]:
    statement = (
        select(PartTable.name, PartTable.uuid, PartTable.model_uuid)
        .offset(page * page_size)
        .limit(page_size)
        .order_by(PartTable.name)
    )
    if name is not None:
        statement = statement.where(PartTable.name == name)
    if uuid is not None:
        statement = statement.where(PartTable.uuid == uuid)
    if model_uuid is not None:
        statement = statement.where(PartTable.model_uuid == model_uuid)
    result = await db_connection.execute(statement)
    return [Part.model_validate(row, from_attributes=True) for row in result]
