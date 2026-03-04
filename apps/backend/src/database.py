"""PostgreSQL data access layer for backend."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

from alembic import command
from alembic.config import Config
from sqlalchemy import Float, ForeignKey, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

DEFAULT_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/esl"


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class Product(Base):
    __tablename__ = "product"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    tags: Mapped[list["Tag"]] = relationship(back_populates="product")


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    current_product_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("product.id"),
        nullable=True,
    )
    battery_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    product: Mapped[Optional[Product]] = relationship(back_populates="tags")


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
        with self._connect() as db_connection:
            with db_connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, name, price FROM product ORDER BY id
                    """
                )
                results = cursor.fetchall()
                return [{
                    "id": row[0],
                    "name": row[1],
                    "price": row[2]}
                    for row in results]

    def update_tag(self, tag_id: int, current_product_id: Optional[int], battery_level: Optional[int]):
        with self._connect() as db_connection:
            with db_connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO tag (id, current_product_id, battery_level)
                    VALUES (%s, %s, %s)
                    ON CONFLICT(id) DO UPDATE
                    SET current_product_id = EXCLUDED.current_product_id,
                        battery_level = EXCLUDED.battery_level
                    """,
                    (tag_id, current_product_id, battery_level),
                )
            db_connection.commit()

    def get_tag(self, tag_id: int) -> Optional[Dict[str, Any]]:
        with self._connect() as db_connection:
            with db_connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, current_product_id, battery_level FROM tag WHERE id = %s
                    """,
                    (tag_id,),
                )
                result = cursor.fetchone()
                if result:
                    return {"id": result[0], "current_product_id": result[1], "battery_level": result[2]}
                return None

    def get_all_tags(self) -> list[Dict[str, Any]]:
        with self._connect() as db_connection:
            with db_connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, current_product_id, battery_level FROM tag ORDER BY id
                    """
                )
                results = cursor.fetchall()
                return [
                    {"id": row[0],
                    "current_product_id": row[1],
                    "battery_level": row[2]}
                    for row in results
                ]

    def testing_records(self):
        """Create starter records used by this sample app."""
        with self._connect() as db_connection:
            with db_connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO product (id, name, price)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (1, "bananas", 10),
                )
                cursor.execute(
                    """
                    INSERT INTO tag (id, current_product_id, battery_level)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (1, 1, None),
                )
            db_connection.commit()
