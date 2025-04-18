from uuid import UUID

from pydantic import BaseModel


class Manufacturer(BaseModel):
    uuid: UUID
    name: str
