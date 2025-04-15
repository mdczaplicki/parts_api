from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils import Timestamp

from parts_api.db import PrimaryKeyUUIDTableMixin, BaseModel


class PartTable(PrimaryKeyUUIDTableMixin, Timestamp, BaseModel):
    name: Mapped[str]
    model_uuid: Mapped[UUID] = mapped_column(
        ForeignKey("model.uuid", ondelete="CASCADE")
    )

    __table_args__ = (
        UniqueConstraint("name", "model_uuid", name="unique_name_and_model_uuid"),
    )
