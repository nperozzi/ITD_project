"""allow many tags to reference one product

Revision ID: 20260304_0002
Revises: 20260304_0001
Create Date: 2026-03-04 00:30:00.000000
"""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260304_0002"
down_revision = "20260304_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE tag DROP CONSTRAINT IF EXISTS tag_current_product_id_key")


def downgrade() -> None:
    op.create_unique_constraint("tag_current_product_id_key", "tag", ["current_product_id"])
