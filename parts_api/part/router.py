from uuid import UUID

from fastapi import APIRouter

from parts_api.part.db import select_parts
from parts_api.part.schema import Part

PART_ROUTER = APIRouter()


@PART_ROUTER.get("/")
async def get_parts(
    name: str | None = None,
    uuid: UUID | None = None,
    model_uuid: UUID | None = None,
    page: int = 0,
    page_size: int = 100,
) -> list[Part]:
    return await select_parts(name, uuid, model_uuid, page, page_size)
