"""Create all tables

Revision ID: d7747549933f
Revises:
Create Date: 2025-04-15 00:29:11.775249

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d7747549933f"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "category",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "uuid",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("updated", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("uuid"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_category_uuid"), "category", ["uuid"], unique=True)
    op.create_table(
        "manufacturer",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "uuid",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("updated", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("uuid"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_manufacturer_uuid"), "manufacturer", ["uuid"], unique=True)
    op.create_table(
        "model",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("manufacturer_uuid", sa.Uuid(), nullable=False),
        sa.Column("category_uuid", sa.Uuid(), nullable=False),
        sa.Column(
            "uuid",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("updated", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["category_uuid"], ["category.uuid"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["manufacturer_uuid"], ["manufacturer.uuid"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("uuid"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_model_uuid"), "model", ["uuid"], unique=True)
    op.create_table(
        "part",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("model_uuid", sa.Uuid(), nullable=False),
        sa.Column(
            "uuid",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("updated", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["model_uuid"], ["model.uuid"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("uuid"),
    )
    op.create_index(op.f("ix_part_uuid"), "part", ["uuid"], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_part_uuid"), table_name="part")
    op.drop_table("part")
    op.drop_index(op.f("ix_model_uuid"), table_name="model")
    op.drop_table("model")
    op.drop_index(op.f("ix_manufacturer_uuid"), table_name="manufacturer")
    op.drop_table("manufacturer")
    op.drop_index(op.f("ix_category_uuid"), table_name="category")
    op.drop_table("category")
    # ### end Alembic commands ###
