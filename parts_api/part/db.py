from sqlalchemy import insert, delete
from sqlalchemy.ext.asyncio import AsyncConnection

from parts_api.db import inject_db_connection
from parts_api.part.schema import CreatePartTuple
from parts_api.part.table import PartTable


@inject_db_connection
async def clear_parts(db_connection: AsyncConnection) -> None:
    statement = delete(PartTable)
    await db_connection.execute(statement)


@inject_db_connection
async def insert_many_parts(
    create_schemas: list[CreatePartTuple], db_connection: AsyncConnection
) -> None:
    statement = (
        insert(PartTable)
        .returning(PartTable.uuid, PartTable.name)
    )
    await db_connection.execute(statement,
            [
                {
                    "name": s.name,
                    "model_uuid": s.model_uuid,
                }
                for s in create_schemas
            ])
