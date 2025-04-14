from typing import NamedTuple
from uuid import UUID


class CreatePartTuple(NamedTuple):
    name: str
    model_uuid: UUID
