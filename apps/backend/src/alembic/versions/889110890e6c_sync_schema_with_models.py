
"""sync schema with models

Revision ID: 889110890e6c
Revises: 20260304_0002
Create Date: 2026-03-05 21:12:27.725406
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '889110890e6c'
down_revision = '20260304_0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('store',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('gateway',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('store_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.Enum('ONLINE', 'OFFLINE', 'DISABLED', name='status'), nullable=False),
    sa.Column('last_heartbeat_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['store_id'], ['store.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('shelfLocation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('store_id', sa.Integer(), nullable=False),
    sa.Column('aisle', sa.Integer(), nullable=False),
    sa.Column('level', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['store_id'], ['store.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('product', sa.Column('sku', sa.String(), nullable=True))
    op.add_column('product', sa.Column('attributes_json', sa.JSON(), nullable=True))
    op.execute("UPDATE product SET sku = 'SKU-' || id::text WHERE sku IS NULL")
    op.execute("UPDATE product SET attributes_json = '{}'::json WHERE attributes_json IS NULL")
    op.alter_column('product', 'sku', existing_type=sa.String(), nullable=False)
    op.alter_column('product', 'attributes_json', existing_type=sa.JSON(), nullable=False)
    op.alter_column('product', 'name',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=False)
    op.add_column('tag', sa.Column('battery_pct', sa.Integer(), nullable=True))
    op.add_column('tag', sa.Column('status', sa.Enum('ONLINE', 'OFFLINE', 'DISABLED', name='status'), nullable=True))
    op.add_column('tag', sa.Column('product_id', sa.Integer(), nullable=True))
    op.add_column('tag', sa.Column('shelf_location_id', sa.Integer(), nullable=True))
    op.execute("UPDATE tag SET battery_pct = battery_level WHERE battery_pct IS NULL")
    op.execute("UPDATE tag SET product_id = current_product_id WHERE product_id IS NULL")
    op.execute("UPDATE tag SET status = 'ONLINE' WHERE status IS NULL")
    op.alter_column('tag', 'status', existing_type=sa.Enum('ONLINE', 'OFFLINE', 'DISABLED', name='status'), nullable=False)
    op.create_check_constraint(
        'ck_tag_battery_pct_0_100',
        'tag',
        'battery_pct IS NULL OR (battery_pct >= 0 AND battery_pct <= 100)',
    )
    op.drop_constraint('tag_current_product_id_fkey', 'tag', type_='foreignkey')
    op.create_foreign_key('fk_tag_product_id_product', 'tag', 'product', ['product_id'], ['id'])
    op.create_foreign_key('fk_tag_shelf_location_id_shelfLocation', 'tag', 'shelfLocation', ['shelf_location_id'], ['id'])
    op.drop_column('tag', 'battery_level')
    op.drop_column('tag', 'current_product_id')


def downgrade() -> None:
    op.add_column('tag', sa.Column('current_product_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('tag', sa.Column('battery_level', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint('fk_tag_shelf_location_id_shelfLocation', 'tag', type_='foreignkey')
    op.drop_constraint('fk_tag_product_id_product', 'tag', type_='foreignkey')
    op.drop_constraint('ck_tag_battery_pct_0_100', 'tag', type_='check')
    op.execute("UPDATE tag SET current_product_id = product_id WHERE current_product_id IS NULL")
    op.execute("UPDATE tag SET battery_level = battery_pct WHERE battery_level IS NULL")
    op.create_foreign_key('tag_current_product_id_fkey', 'tag', 'product', ['current_product_id'], ['id'])
    op.drop_column('tag', 'shelf_location_id')
    op.drop_column('tag', 'product_id')
    op.drop_column('tag', 'status')
    op.drop_column('tag', 'battery_pct')
    op.alter_column('product', 'name',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)
    op.drop_column('product', 'attributes_json')
    op.drop_column('product', 'sku')
    op.drop_table('shelfLocation')
    op.drop_table('gateway')
    op.drop_table('store')
    op.execute("DROP TYPE IF EXISTS status")
