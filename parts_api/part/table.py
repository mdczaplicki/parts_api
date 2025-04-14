from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils import Timestamp

from parts_api.db import PrimaryKeyUUIDTableMixin, BaseModel


class PartTable(PrimaryKeyUUIDTableMixin, Timestamp, BaseModel):
    name: Mapped[str] = mapped_column(unique=True)
    model_uuid: Mapped[UUID] = mapped_column(ForeignKey("model.uuid"))
