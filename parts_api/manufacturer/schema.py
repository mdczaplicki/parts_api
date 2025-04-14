from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CreateManufacturerPayload(BaseModel):
    name: str


class Manufacturer(BaseModel):
    uuid: UUID
    created: datetime
    updated: datetime
    name: str
