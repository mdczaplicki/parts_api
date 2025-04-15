from uuid import UUID

from fastapi import APIRouter

from parts_api.model.db import select_models
from parts_api.model.schema import Model

MODEL_ROUTER = APIRouter()


@MODEL_ROUTER.get("/")
async def get_models(
    name: str | None = None,
    uuid: UUID | None = None,
    manufacturer_uuid: UUID | None = None,
    category_uuid: UUID | None = None,
) -> list[Model]:
    return await select_models(name, uuid, manufacturer_uuid, category_uuid)
