"""rename promotion discount_pct column back to discount_percentage

Revision ID: 20260315_0004
Revises: 20260314_0003
Create Date: 2026-03-15 10:20:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260315_0004"
down_revision = "20260314_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "promotion",
        "discount_pct",
        new_column_name="discount_percentage",
        existing_type=sa.Integer(),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "promotion",
        "discount_percentage",
        new_column_name="discount_pct",
        existing_type=sa.Integer(),
        existing_nullable=False,
    )
