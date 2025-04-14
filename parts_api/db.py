import re
from uuid import UUID, uuid4

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column
from sqlalchemy.util import generic_repr


camel_case_to_snake_case_pattern = re.compile(r"(?<!^)(?=[A-Z])")


@generic_repr
class BaseModel(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        name_without_table = cls.__name__.replace("Table", "")
        return camel_case_to_snake_case_pattern.sub("_", name_without_table).lower()


class PrimaryKeyUUIDTableMixin:
    uuid: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        server_default=func.gen_random_uuid(),
        unique=True,
        index=True,
    )
