import re
from contextlib import asynccontextmanager
from functools import lru_cache, wraps
from inspect import signature
from typing import AsyncGenerator, TypeVar, Callable, Any
from uuid import UUID, uuid4

from sqlalchemy import func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncConnection
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column

from parts_api.settings.db import DATABASE_SETTINGS

camel_case_to_snake_case_pattern = re.compile(r"(?<!^)(?=[A-Z])")

F = TypeVar("F", bound=Callable[..., Any])


class BaseModel(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        name_without_table = cls.__name__.replace("Table", "")
        return camel_case_to_snake_case_pattern.sub("_", name_without_table).lower()


class PrimaryKeyUUIDTableMixin:
    uuid: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        server_default=func.gen_random_uuid(),
        unique=True,
        index=True,
    )


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    engine: AsyncEngine = create_async_engine(
        DATABASE_SETTINGS.connection_string,
        pool_size=DATABASE_SETTINGS.connection_pool_size,
        max_overflow=DATABASE_SETTINGS.connection_pool_max_overflow,
    )
    return engine


@asynccontextmanager
async def db_connection() -> AsyncGenerator[AsyncConnection, None]:
    engine = get_engine()
    async with engine.connect() as connection:
        try:
            yield connection
            await connection.commit()
        except Exception:
            await connection.rollback()
            raise
        finally:
            await connection.close()


def inject_db_connection(function: F):
    @wraps(function)
    async def wrapper(*args, **kwargs):
        if "db_connection" in kwargs:
            return await function(*args, **kwargs)
        passed_args = dict(zip(signature(function).parameters, args, strict=False))
        if "db_connection" in passed_args:
            return await function(*args, **kwargs)
        async with db_connection() as connection:
            return await function(*args, **kwargs, db_connection=connection)

    wrapper: function  # type: ignore[no-redef, valid-type]
    return wrapper
