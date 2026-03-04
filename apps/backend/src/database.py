"""SQLite data access layer for backend.

import os
from typing import Any, Dict, Optional
import psycopg2

class BackendDB:
    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL")
        self._create_schema()
        self.testing_records()

    def _connect(self):
        return psycopg2.connect(self.database_url, connect_timeout=5)

    def _create_schema(self) -> None:
        with self._connect() as db_connection:
            with db_connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS product (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        price DOUBLE PRECISION NOT NULL
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tag (
                        id INTEGER PRIMARY KEY,
                        current_product_id INTEGER UNIQUE,
                        battery_level INTEGER,
                        FOREIGN KEY (current_product_id) REFERENCES product(id)
                    )
                    """
                )
            db_connection.commit()

    

    def set_product_price(self, product_id: int, price: float) -> None:
        with self._connect() as db_connection:
            with db_connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE product SET price = %s WHERE id = %s
                    """,
                    (price, product_id),
                )
            db_connection.commit()

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
