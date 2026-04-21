"""Alembic migration environment.

Imports every feature `schema` module so `Base.metadata` contains all tables
before autogenerate runs.
"""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from db.base import Base

# Importing feature schemas registers their ORM models on Base.metadata.
# Schemas are added as features come online; imports are guarded to avoid
# crashing migrations before a given feature exists.
try:
    from features.tag_registry import schema as _tag_registry_schema  # noqa: F401
except ImportError:
    pass
try:
    from features.payload_delivery import schema as _payload_delivery_schema  # noqa: F401
except ImportError:
    pass


config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
