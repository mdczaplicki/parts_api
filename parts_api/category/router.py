from uuid import UUID

from fastapi import APIRouter

from parts_api.category.db import select_categories
from parts_api.category.schema import Category

CATEGORY_ROUTER = APIRouter()


@CATEGORY_ROUTER.get("/")
async def get_categories(
    name: str | None = None, uuid: UUID | None = None
) -> list[Category]:
    return await select_categories(name, uuid)
