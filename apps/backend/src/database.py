"""PostgreSQL data access layer for backend."""

from __future__ import annotations

import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from seeds.demo_data import seed_demo_data

DEFAULT_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/esl"


def _database_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def run_migrations() -> None:
    """Apply Alembic migrations to latest revision before app starts."""
    alembic_ini = Path(__file__).with_name("alembic.ini")
    if not alembic_ini.exists():
        raise RuntimeError(f"Alembic config was not found at {alembic_ini}")

    alembic_config = Config(str(alembic_ini))
    alembic_config.set_main_option("sqlalchemy.url", _database_url())
    command.upgrade(alembic_config, "head")


class BackendDB:
    def __init__(self) -> None:
        self.database_url = _database_url()
        self.engine = create_engine(self.database_url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)
        self.seed_records()

    def seed_records(self) -> None:
        """Create or refresh stable demo records used by this sample app."""
        with self.SessionLocal() as session:
            seed_demo_data(session)
