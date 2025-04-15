import asyncio
from asyncio import BoundedSemaphore
from time import time
from typing import Final, NamedTuple
from uuid import UUID

from aiohttp import ClientSession
from bs4 import BeautifulSoup, Tag, SoupStrainer
from yarl import URL

from parts_api.category.db import insert_many_categories, clear_categories
from parts_api.manufacturer.db import insert_many_manufacturers, clear_manufacturers
from parts_api.model.db import clear_models, insert_many_models
from parts_api.model.schema import CreateModelTuple
from parts_api.part.db import insert_many_parts
from parts_api.part.schema import CreatePartTuple

_BASE_URL: Final[URL] = URL("https://www.urparts.com/")
_CATALOGUE_PATH: Final[str] = "index.cfm/page/catalogue"
_SEMAPHORE = BoundedSemaphore(50)


class TagInfo(NamedTuple):
    name: str
    path: str


async def _get_tag_from_url(session: ClientSession, url: URL) -> Tag:
    async with _SEMAPHORE:
        async with session.get(url) as response:
            content = await response.text()
    strainer = SoupStrainer(id="content")
    return BeautifulSoup(content, "html.parser", parse_only=strainer)


async def _get_tag(session: ClientSession, path: str) -> Tag:
    return await _get_tag_from_url(session, _BASE_URL / path)


def stream_manufacturers(catalogue_tag: Tag):
    for tag in catalogue_tag.select("div.allmakes > * a"):
        yield TagInfo(tag.text.strip(), tag["href"])


def stream_categories(tag: Tag):
    for tag in tag.select("div.allcategories > * a"):
        yield TagInfo(tag.text.strip(), tag["href"])


def stream_models(tag: Tag):
    for tag in tag.select("div.allmodels > * a"):
        yield TagInfo(tag.text.strip(), tag["href"])


def stream_parts(tag: Tag):
    for tag in tag.select("div.allparts > * a"):
        part_number = tag.text.split("-")[0].strip()
        yield TagInfo(part_number, tag["href"])


async def process_model(
    session: ClientSession, model: TagInfo, model_uuid: UUID
) -> list[CreatePartTuple]:
    model_tag = await _get_tag(session, model.path)
    insert_buffer: list[CreatePartTuple] = []

    for part in stream_parts(model_tag):
        if part.name is None:
            print(model.name)
        insert_buffer.append(CreatePartTuple(part.name, model_uuid))

    return insert_buffer


async def process_category(
    session: ClientSession,
    category: TagInfo,
    manufacturer_uuid: UUID,
    category_name_to_uuid: dict[str, UUID],
) -> None:
    category_tag = await _get_tag(session, category.path)
    models = list(stream_models(category_tag))

    if not models:
        return
    model_name_to_uuid = await insert_many_models(
        [
            CreateModelTuple(
                name=m.name,
                manufacturer_uuid=manufacturer_uuid,
                category_uuid=category_name_to_uuid[category.name],
            )
            for m in models
        ]
    )

    insert_buffers = await asyncio.gather(
        *(
            process_model(session, model, model_name_to_uuid[model.name])
            for model in models
        )
    )
    for insert_buffer in insert_buffers:
        if insert_buffer:
            await insert_many_parts(insert_buffer)


async def process_manufacturer(
    session: ClientSession,
    manufacturer: TagInfo,
    manufacturer_uuid: UUID,
    category_name_to_uuid: dict[str, UUID],
) -> dict[str, UUID]:
    manufacturer_tag = await _get_tag(session, manufacturer.path)

    categories = list(stream_categories(manufacturer_tag))
    category_name_to_uuid |= await insert_many_categories({c.name for c in categories})

    await asyncio.gather(
        *(
            process_category(
                session, category, manufacturer_uuid, category_name_to_uuid
            )
            for category in categories
        )
    )
    return category_name_to_uuid


async def main():
    start = time()
    async with ClientSession() as session:
        catalogue_tag = await _get_tag(session, _CATALOGUE_PATH)
        manufacturers = list(stream_manufacturers(catalogue_tag))

        await clear_manufacturers()
        manufacturer_name_to_uuid = await insert_many_manufacturers(
            [m.name for m in manufacturers]
        )

        await clear_categories()
        await clear_models()
        category_name_to_uuid = {}

        for manufacturer in manufacturers:
            if manufacturer.name != "Volvo":
                continue
            print(f"Processing: {manufacturer.name}")
            category_name_to_uuid = await process_manufacturer(
                session,
                manufacturer,
                manufacturer_name_to_uuid[manufacturer.name],
                category_name_to_uuid,
            )

    print("Done. Total time:", time() - start)


if __name__ == "__main__":
    asyncio.run(main())
