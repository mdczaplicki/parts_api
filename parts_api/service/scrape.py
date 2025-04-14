import asyncio
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


async def get_parts(
        session: ClientSession, path: str
) -> AsyncGenerator[TagInfo, None]:
    url = _BASE_URL / path
    soup = await _get_soup_from_url(session, url)
    tags = soup.select("div.allparts > * a")
    for tag in tags:
        part_number = tag.text.split("-")[0].strip()
        yield TagInfo(name=part_number, path=tag["href"])


async def main() -> None:
    async with ClientSession() as session:
        async for manufacturer in get_all_manufacturers(session):
            async for category in get_categories(session, manufacturer.path):
                async for model in get_models(session, category.path):
                    async for part in get_parts(session, model.path):
                        print(part)


if __name__ == "__main__":
    asyncio.run(main())
