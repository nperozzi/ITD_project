from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from db.models.gateway import Gateway, Status as GatewayStatus
from db.models.product import Product
from db.models.promotion import Promotion
from db.models.shelfLocation import ShelfLocation
from db.models.store import Store
from db.models.tag import Status as TagStatus, Tag
from db.models.tagpayload import TagPayload


def seed_demo_data(session: Session) -> None:
    """Insert or update a stable demo dataset for local development."""
    _upsert_stores(session)
    _upsert_gateways(session)
    _upsert_shelf_locations(session)
    _upsert_products(session)
    _upsert_tags(session)
    _upsert_promotions(session)
    _upsert_tagpayloads(session)
    session.commit()


def _upsert_stores(session: Session) -> None:
    _upsert(
        session,
        Store,
        1,
        {"name": "Downtown Market"},
    )
    _upsert(
        session,
        Store,
        2,
        {"name": "Riverside Market"},
    )


def _upsert_gateways(session: Session) -> None:
    _upsert(
        session,
        Gateway,
        1,
        {
            "store_id": 1,
            "status": GatewayStatus.ONLINE,
            "last_heartbeat_at": datetime(2026, 2, 26, 9, 15, 0),
        },
    )
    _upsert(
        session,
        Gateway,
        2,
        {
            "store_id": 1,
            "status": GatewayStatus.DISABLED,
            "last_heartbeat_at": datetime(2026, 2, 26, 9, 10, 0),
        },
    )
    _upsert(
        session,
        Gateway,
        3,
        {
            "store_id": 2,
            "status": GatewayStatus.OFFLINE,
            "last_heartbeat_at": datetime(2026, 2, 26, 8, 2, 0),
        },
    )


def _upsert_shelf_locations(session: Session) -> None:
    _upsert(session, ShelfLocation, 1, {"store_id": 1, "aisle": 1, "level": 1})
    _upsert(session, ShelfLocation, 2, {"store_id": 1, "aisle": 2, "level": 2})
    _upsert(session, ShelfLocation, 3, {"store_id": 2, "aisle": 1, "level": 1})


def _upsert_products(session: Session) -> None:
    _upsert(
        session,
        Product,
        1,
        {
            "sku": "CF-AR-1KG",
            "name": "Arabica Coffee Beans",
            "attributes_json": {"roast": "medium", "origin": "Colombia", "organic": True},
            "price": 22.9,
        },
    )
    _upsert(
        session,
        Product,
        2,
        {
            "sku": "ML-OT-1L",
            "name": "Organic Oat Milk",
            "attributes_json": {"dairyFree": True, "volumeMl": 1000},
            "price": 4.5,
        },
    )
    _upsert(
        session,
        Product,
        3,
        {
            "sku": "CH-DK-90G",
            "name": "Dark Chocolate Bar",
            "attributes_json": {"cocoaPct": 75, "vegan": True},
            "price": 3.2,
        },
    )


def _upsert_tags(session: Session) -> None:
    _upsert(
        session,
        Tag,
        1,
        {
            "battery_pct": 88,
            "status": TagStatus.ONLINE,
            "product_id": 1,
            "shelf_location_id": 1,
        },
    )
    _upsert(
        session,
        Tag,
        2,
        {
            "battery_pct": 24,
            "status": TagStatus.ONLINE,
            "product_id": 2,
            "shelf_location_id": 2,
        },
    )
    _upsert(
        session,
        Tag,
        3,
        {
            "battery_pct": 0,
            "status": TagStatus.OFFLINE,
            "product_id": 3,
            "shelf_location_id": 3,
        },
    )


def _upsert_promotions(session: Session) -> None:
    _upsert(
        session,
        Promotion,
        1,
        {
            "product_id": 1,
            "discount_pct": 10,
            "start_at": datetime(2026, 2, 25, 0, 0, 0),
            "end_at": datetime(2026, 3, 3, 23, 59, 59),
        },
    )
    _upsert(
        session,
        Promotion,
        2,
        {
            "product_id": 3,
            "discount_pct": 15,
            "start_at": datetime(2026, 2, 26, 0, 0, 0),
            "end_at": datetime(2026, 3, 1, 23, 59, 59),
        },
    )


def _upsert_tagpayloads(session: Session) -> None:
    _upsert(
        session,
        TagPayload,
        1,
        {
            "tag_id": 1,
            "payload_json": {
                "tagId": 1,
                "title": "Arabica Coffee Beans",
                "basePrice": 22.9,
                "finalPrice": 20.61
                },
        },
    )
    _upsert(
        session,
        TagPayload,
        2,
        {
            "tag_id": 2,
            "payload_json": {
                "tagId": 2,
                "title": "Organic Oat Milk",
                "basePrice": 4.5,
                "finalPrice": 4.5
                },
        },
    )


def _upsert(session: Session, model: type, record_id: int, values: dict) -> None:
    record = session.get(model, record_id)
    if record is None:
        record = model(id=record_id, **values)
        session.add(record)
        return

    for key, value in values.items():
        setattr(record, key, value)
