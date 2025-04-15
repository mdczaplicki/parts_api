from uuid import UUID

from pydantic import BaseModel


class Category(BaseModel):
    uuid: UUID
    name: str
