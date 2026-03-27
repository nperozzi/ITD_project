"""rename promotion discount_percentage column to discount_percentage

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
    # The table already uses discount_percentage in the previous revision.
    # Keep this revision as a no-op so fresh databases can migrate cleanly.
    pass


def downgrade() -> None:
    pass
