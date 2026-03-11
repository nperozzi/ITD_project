"""PostgreSQL data access layer for backend."""

from __future__ import annotations

import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Product, Tag
from db.models.tag import Status

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
        self.testing_records()

    def testing_records(self) -> None:
        """Create starter records used by this sample app."""
        with self.SessionLocal() as session:
            product = session.get(Product, 1)
            if product is None:
                product = Product(
                    id=1,
                    sku="BAN-001",
                    name="bananas",
                    attributes_json={},
                    price=10,
                )
                session.add(product)

            tag = session.get(Tag, 1)
            if tag is None:
                tag = Tag(
                    id=1,
                    battery_pct=None,
                    status=Status.ONLINE,
                    product_id=1,
                    shelf_location_id=None,
                )
                session.add(tag)

            session.commit()
