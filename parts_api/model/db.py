from uuid import UUID

from sqlalchemy import insert, delete
from sqlalchemy.ext.asyncio import AsyncConnection

from parts_api.db import inject_db_connection
from parts_api.model.schema import CreateModelTuple
from parts_api.model.table import ModelTable


@inject_db_connection
async def clear_models(db_connection: AsyncConnection) -> None:
    statement = delete(ModelTable)
    await db_connection.execute(statement)


@inject_db_connection
async def insert_many_models(
    create_schemas: list[CreateModelTuple], db_connection: AsyncConnection
) -> dict[str, UUID]:
    statement = (
        insert(ModelTable)
        .values(
            [
                {
                    ModelTable.name: s.name,
                    ModelTable.category_uuid: s.category_uuid,
                    ModelTable.manufacturer_uuid: s.manufacturer_uuid,
                }
                for s in create_schemas
            ]
        )
        .returning(ModelTable.uuid, ModelTable.name)
    )
    result = await db_connection.execute(statement)
    return {row.name: row.uuid for row in result}
