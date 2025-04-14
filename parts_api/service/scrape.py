import asyncio
from asyncio import TaskGroup
from time import time
from typing import Final, AsyncGenerator

from aiohttp import ClientSession
from bs4 import BeautifulSoup
from pydantic import BaseModel
from yarl import URL

_BASE_URL: Final[URL] = URL("https://www.urparts.com/")
_CATALOGUE_PATH: Final[str] = "index.cfm/page/catalogue"


class TagInfo(BaseModel):
    name: str
    path: str


async def _get_soup_from_url(session: ClientSession, url: URL) -> BeautifulSoup:
    response = await session.get(url)
    content = await response.text()
    return BeautifulSoup(content, "html.parser")


async def get_all_manufacturers(
    session: ClientSession,
) -> AsyncGenerator[TagInfo, None]:
    url = _BASE_URL / _CATALOGUE_PATH
    soup = await _get_soup_from_url(session, url)
    tags = soup.select("div.allmakes > * a")
    for tag in tags:
        yield TagInfo(name=tag.text.strip(), path=tag["href"])


async def get_categories(
    session: ClientSession, path: str
) -> AsyncGenerator[TagInfo, None]:
    url = _BASE_URL / path
    soup = await _get_soup_from_url(session, url)
    tags = soup.select("div.allcategories > * a")
    for tag in tags:
        yield TagInfo(name=tag.text.strip(), path=tag["href"])


async def get_models(
    session: ClientSession, path: str
) -> AsyncGenerator[TagInfo, None]:
    url = _BASE_URL / path
    soup = await _get_soup_from_url(session, url)
    tags = soup.select("div.allmodels > * a")
    for tag in tags:
        yield TagInfo(name=tag.text.strip(), path=tag["href"])


async def get_parts(session: ClientSession, path: str) -> AsyncGenerator[TagInfo, None]:
    url = _BASE_URL / path
    soup = await _get_soup_from_url(session, url)
    tags = soup.select("div.allparts > * a")
    for tag in tags:
        part_number = tag.text.split("-")[0].strip()
        yield TagInfo(name=part_number, path=tag["href"])


async def main() -> None:
    parts = []
    now = time()
    async with ClientSession() as session:
        category_tasks = set()
        async with TaskGroup() as category_task_group:
            async for manufacturer in get_all_manufacturers(session):
                if manufacturer.name != "Ammann":
                    break
                category_tasks.add(category_task_group.create_task(
                    get_categories(session, manufacturer.path)
                ))
        model_tasks =set()
        async with TaskGroup() as model_task_group:
            for category_task in category_tasks:
                for category in category_task.result():
                    model_tasks.add(model_task_group.create_task(get_models(session, category.path)))
        part_tasks = set()
        async with TaskGroup() as part_task_group:
            for model_task in model_tasks:
                for model in model_task.result():
                    part_tasks.add(part_task_group.create_task(get_parts(session, model.path)))
        for part_task in part_tasks:
            for part in part_task.result():
                parts.append(part)

    print("Processing time: ", time() - now)
    print("Number of parts: ", len(parts))


if __name__ == "__main__":
    asyncio.run(main())
