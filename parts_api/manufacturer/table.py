from sqlalchemy.orm import Mapped
from sqlalchemy_utils import Timestamp

from parts_api.db import PrimaryKeyUUIDTableMixin, BaseModel


class ManufacturerTable(PrimaryKeyUUIDTableMixin, Timestamp, BaseModel):
    name: Mapped[str]
