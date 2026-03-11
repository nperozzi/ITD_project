"""create product and tag tables

Revision ID: 20260304_0001
Revises:
Create Date: 2026-03-04 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260304_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "product",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
    )

    op.create_table(
        "tag",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("current_product_id", sa.Integer(), nullable=True, unique=True),
        sa.Column("battery_level", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["current_product_id"], ["product.id"]),
    )


def downgrade() -> None:
    op.drop_table("tag")
    op.drop_table("product")
