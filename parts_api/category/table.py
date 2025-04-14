from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils import Timestamp

from parts_api.db import PrimaryKeyUUIDTableMixin, BaseModel


class CategoryTable(PrimaryKeyUUIDTableMixin, Timestamp, BaseModel):
    name: Mapped[str] = mapped_column(unique=True)
