import asyncio
from asyncio import TaskGroup, BoundedSemaphore
from time import time
from typing import Final, Generator, NamedTuple

from aiohttp import ClientSession
from bs4 import BeautifulSoup, Tag
from yarl import URL

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
        manufacturer_tag_tasks = []
        print(".")
        async with TaskGroup() as task_group:
            for manufacturer in stream_manufacturers(catalogue_tag):
                if manufacturer.name != "Volvo":
                    continue
                manufacturer_tag_tasks.append(
                    task_group.create_task(_get_tag(session, manufacturer.path))
                )
        print(".")
        category_tag_tasks = []
        async with TaskGroup() as task_group:
            for manufacturer_task in manufacturer_tag_tasks:
                for category in stream_categories(manufacturer_task.result()):
                    category_tag_tasks.append(
                        task_group.create_task(_get_tag(session, category.path))
                    )
        print(".")
        model_tag_tasks = []
        async with TaskGroup() as task_group:
            for category_task in category_tag_tasks:
                for model in stream_models(category_task.result()):
                    model_tag_tasks.append(
                        task_group.create_task(_get_tag(session, model.path))
                    )
        print(".")
        for model_task in model_tag_tasks:
            for part in stream_parts(model_task.result()):
                ...

    print("Processing time: ", time() - now)


if __name__ == "__main__":
    asyncio.run(main())
