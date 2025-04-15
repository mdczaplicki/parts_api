from typing import NamedTuple
from uuid import UUID

from pydantic import BaseModel


class CreatePartTuple(NamedTuple):
    name: str
    model_uuid: UUID


class Part(BaseModel):
    uuid: UUID
    name: str
    model_uuid: UUID
