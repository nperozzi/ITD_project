"""Alembic migration helper.

Lets the gateway daemon apply pending migrations at startup without shelling out
to the `alembic` CLI. Paths are resolved relative to `apps/gateway/` so the
helper works both in Docker (workdir `/app`) and when running from source.
"""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config

from logger import Logger


def run_migrations(database_url: str, logger: Logger | None = None) -> None:
    active_logger = logger or Logger("gateway.migrations")
    gateway_root = Path(__file__).resolve().parent.parent.parent
    alembic_config_path = gateway_root / "alembic.ini"

    alembic_config = Config(str(alembic_config_path))
    alembic_config.set_main_option("script_location", str(gateway_root / "migrations"))
    alembic_config.set_main_option("sqlalchemy.url", database_url)

    active_logger.info("applying alembic migrations (db=%s)", database_url)
    command.upgrade(alembic_config, "head")
    active_logger.info("migrations up to date")
