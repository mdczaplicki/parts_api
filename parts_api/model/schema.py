from typing import NamedTuple
from uuid import UUID

from pydantic import BaseModel


class CreateModelTuple(NamedTuple):
    name: str
    manufacturer_uuid: UUID
    category_uuid: UUID


class Model(BaseModel):
    uuid: UUID
    name: str
    manufacturer_uuid: UUID
    category_uuid: UUID
