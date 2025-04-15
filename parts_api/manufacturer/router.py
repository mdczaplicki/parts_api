from uuid import UUID

from fastapi import APIRouter

from parts_api.manufacturer.db import select_manufacturers
from parts_api.manufacturer.schema import Manufacturer

MANUFACTURER_ROUTER = APIRouter()


@MANUFACTURER_ROUTER.get("/")
async def get_manufacturers(
    name: str | None = None, uuid: UUID | None = None
) -> list[Manufacturer]:
    return await select_manufacturers(name, uuid)
