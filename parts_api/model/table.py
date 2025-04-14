from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils import Timestamp

from parts_api.db import PrimaryKeyUUIDTableMixin, BaseModel


class ModelTable(PrimaryKeyUUIDTableMixin, Timestamp, BaseModel):
    name: Mapped[str] = mapped_column(unique=True)
    manufacturer_uuid: Mapped[UUID] = mapped_column(
        ForeignKey("manufacturer.uuid", ondelete="CASCADE")
    )
    category_uuid: Mapped[UUID] = mapped_column(
        ForeignKey("category.uuid", ondelete="CASCADE")
    )
