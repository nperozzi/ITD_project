"""rename promotion discount_percentage column to discount_pct

Revision ID: 20260314_0003
Revises: 0da8c32c0e7a
Create Date: 2026-03-14 18:35:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260314_0003"
down_revision = "0da8c32c0e7a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "promotion",
        "discount_percentage",
        new_column_name="discount_pct",
        existing_type=sa.Integer(),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "promotion",
        "discount_pct",
        new_column_name="discount_percentage",
        existing_type=sa.Integer(),
        existing_nullable=False,
    )
