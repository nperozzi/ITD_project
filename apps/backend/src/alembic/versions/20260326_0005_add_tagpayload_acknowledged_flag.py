"""add acknowledged flag to tagpayload

Revision ID: 20260326_0005
Revises: 20260315_0004
Create Date: 2026-03-26 16:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260326_0005"
down_revision = "20260315_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tagpayload",
        sa.Column("acknowledged", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("tagpayload", "acknowledged", server_default=None)


def downgrade() -> None:
    op.drop_column("tagpayload", "acknowledged")
