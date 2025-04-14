import asyncio
from asyncio import TaskGroup, BoundedSemaphore, Task
from time import time
from typing import Final, Generator, NamedTuple

from aiohttp import ClientSession
from bs4 import BeautifulSoup, Tag
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
        response = await session.get(url)
        content = await response.text()
    html_soup = BeautifulSoup(content, "html.parser")
    return html_soup.select_one("#content")


async def _get_tag(session: ClientSession, path: str) -> Tag:
    return await _get_tag_from_url(session, _BASE_URL / path)


def stream_manufacturers(catalogue_tag: Tag) -> Generator[TagInfo, None, None]:
    tags = catalogue_tag.select("div.allmakes > * a")
    for tag in tags:
        yield TagInfo(name=tag.text.strip(), path=tag["href"])


def stream_categories(manufacturer_tag: Tag) -> Generator[TagInfo, None, None]:
    tags = manufacturer_tag.select("div.allcategories > * a")
    for tag in tags:
        yield TagInfo(name=tag.text.strip(), path=tag["href"])


def stream_models(category_tag: Tag) -> Generator[TagInfo, None, None]:
    tags = category_tag.select("div.allmodels > * a")
    for tag in tags:
        yield TagInfo(name=tag.text.strip(), path=tag["href"])


def stream_parts(model_tag: Tag) -> Generator[TagInfo, None, None]:
    tags = model_tag.select("div.allparts > * a")
    for tag in tags:
        part_number = tag.text.split("-")[0].strip()
        yield TagInfo(name=part_number, path=tag["href"])


async def main() -> None:
    now = time()
    async with ClientSession() as session:
        catalogue_tag = await _get_tag(session, _CATALOGUE_PATH)
        manufacturer_tasks: list[tuple[str, Task]] = []
        print(".")
        async with TaskGroup() as task_group:
            for manufacturer in stream_manufacturers(catalogue_tag):
                if manufacturer.name != "Ammann":
                    continue
                manufacturer_tasks.append(
                    (
                        manufacturer.name,
                        task_group.create_task(_get_tag(session, manufacturer.path)),
                    )
                )
        print(".")
        await clear_manufacturers()
        manufacturer_name_to_uuid = await insert_many_manufacturers(
            [name for name, _ in manufacturer_tasks]
        )
        print(manufacturer_name_to_uuid)
        category_tasks: list[tuple[str, str, Task]] = []
        async with TaskGroup() as task_group:
            for (
                manufacturer_name,
                manufacturer_task,
            ) in manufacturer_tasks:
                for category in stream_categories(manufacturer_task.result()):
                    category_tasks.append(
                        (
                            manufacturer_name,
                            category.name,
                            task_group.create_task(_get_tag(session, category.path)),
                        )
                    )
        print(".")
        await clear_categories()
        category_name_to_uuid = await insert_many_categories(
            [name for _, name, __ in category_tasks]
        )
        print(category_name_to_uuid)
        model_tasks: list[tuple[str, str, str, Task]] = []
        async with TaskGroup() as task_group:
            for manufacturer_name, category_name, category_task in category_tasks:
                for model in stream_models(category_task.result()):
                    model_tasks.append(
                        (
                            manufacturer_name,
                            category_name,
                            model.name,
                            task_group.create_task(_get_tag(session, model.path)),
                        )
                    )
        print(".")
        await clear_models()
        model_name_to_uuid = await insert_many_models(
            [
                CreateModelTuple(
                    name=model_name,
                    manufacturer_uuid=manufacturer_name_to_uuid[manufacturer_name],
                    category_uuid=category_name_to_uuid[category_name],
                )
                for manufacturer_name, category_name, model_name, _ in model_tasks
            ]
        )
        print(model_name_to_uuid)
        for manufacturer_name, category_name, model_name, model_task in model_tasks:
            insert_buffer = []
            for part in stream_parts(model_task.result()):
                insert_buffer.append(
                    CreatePartTuple(part.name, model_name_to_uuid[model_name])
                )
                if len(insert_buffer) >= 50:
                    await insert_many_parts(insert_buffer)
                    insert_buffer = []

    print("Processing time: ", time() - now)


if __name__ == "__main__":
    asyncio.run(main())
