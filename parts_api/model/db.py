from uuid import UUID

from sqlalchemy import insert, delete, select
from sqlalchemy.ext.asyncio import AsyncConnection

from parts_api.db import inject_db_connection
from parts_api.model.schema import CreateModelTuple, Model
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


@inject_db_connection
async def select_models(
    name: str | None,
    uuid: UUID | None,
    manufacturer_uuid: UUID | None,
    category_uuid: UUID | None,
    db_connection: AsyncConnection,
) -> list[Model]:
    statement = select(
        ModelTable.name,
        ModelTable.uuid,
        ModelTable.manufacturer_uuid,
        ModelTable.category_uuid,
    )
    if name is not None:
        statement = statement.where(ModelTable.name == name)
    if uuid is not None:
        statement = statement.where(ModelTable.uuid == uuid)
    if manufacturer_uuid is not None:
        statement = statement.where(ModelTable.manufacturer_uuid == manufacturer_uuid)
    if category_uuid is not None:
        statement = statement.where(ModelTable.category_uuid == category_uuid)
    result = await db_connection.execute(statement)
    return [Model.model_validate(row, from_attributes=True) for row in result]
