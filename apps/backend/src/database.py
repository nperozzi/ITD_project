"""PostgreSQL data access layer for backend."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from db.models import Product, Tag

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

    def set_product_price(self, product_id: int, price: float) -> None:
        with self.SessionLocal() as session:
            product = session.get(Product, product_id)
            if product is None:
                return

            product.price = float(price)
            session.commit()

    def get_all_products(self) -> list[Dict[str, Any]]:
        with self.SessionLocal() as session:
            products = session.scalars(select(Product).order_by(Product.id)).all()
            return [
                {
                    "id": row.id,
                    "name": row.name,
                    "price": row.price,
                }
                for row in products
            ]

    def update_tag(self, tag_id: int, current_product_id: Optional[int], battery_level: Optional[int]) -> None:
        with self.SessionLocal() as session:
            tag = session.get(Tag, tag_id)
            if tag is None:
                tag = Tag(id=tag_id)
                session.add(tag)

            tag.current_product_id = current_product_id
            tag.battery_level = battery_level
            session.commit()

    def get_tag(self, tag_id: int) -> Optional[Dict[str, Any]]:
        with self.SessionLocal() as session:
            tag = session.get(Tag, tag_id)
            if tag is None:
                return None
            return {
                "id": tag.id,
                "current_product_id": tag.current_product_id,
                "battery_level": tag.battery_level,
            }

    def get_all_tags(self) -> list[Dict[str, Any]]:
        with self.SessionLocal() as session:
            tags = session.scalars(select(Tag).order_by(Tag.id)).all()
            return [
                {
                    "id": row.id,
                    "current_product_id": row.current_product_id,
                    "battery_level": row.battery_level,
                }
                for row in tags
            ]

    def testing_records(self) -> None:
        """Create starter records used by this sample app."""
        with self.SessionLocal() as session:
            product = session.get(Product, 1)
            if product is None:
                product = Product(id=1, name="bananas", price=10)
                session.add(product)

            tag = session.get(Tag, 1)
            if tag is None:
                tag = Tag(id=1, current_product_id=1, battery_level=None)
                session.add(tag)

            session.commit()
