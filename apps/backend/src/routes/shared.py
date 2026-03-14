from __future__ import annotations

from contextlib import contextmanager

from flask import current_app


@contextmanager
def session_scope():
    db = current_app.config.get("db")
    if db is None:
        raise RuntimeError("Database is not configured for this app.")

    with db.SessionLocal() as session:
        yield session


def dashboard_data() -> dict[str, list[dict[str, object]]]:
    return {
        "stores": [
            {"id": "store-001", "name": "Downtown Market"},
            {"id": "store-002", "name": "Riverside Market"},
        ],
        "gateways": [
            {
                "id": "gw-001",
                "storeId": "store-001",
                "status": "online",
                "lastHeartbeatAt": "2026-02-26T09:15:00Z",
            },
            {
                "id": "gw-002",
                "storeId": "store-001",
                "status": "degraded",
                "lastHeartbeatAt": "2026-02-26T09:10:00Z",
            },
            {
                "id": "gw-003",
                "storeId": "store-002",
                "status": "offline",
                "lastHeartbeatAt": "2026-02-26T08:02:00Z",
            },
        ],
        "shelfLocations": [
            {"id": "sl-001", "storeId": "store-001", "aisle": "A1", "level": "L1"},
            {"id": "sl-002", "storeId": "store-001", "aisle": "A2", "level": "L2"},
            {"id": "sl-003", "storeId": "store-002", "aisle": "B1", "level": "L1"},
        ],
        "tagPayloads": [
            {
                "id": "tp-001",
                "payloadJson": {"tagId": "tag-001", "title": "Arabica Coffee Beans", "price": 22.9},
            },
            {
                "id": "tp-002",
                "payloadJson": {"tagId": "tag-002", "title": "Organic Oat Milk", "price": 4.5},
            },
        ],
        "promotions": [
            {
                "id": "promo-001",
                "productId": "prd-001",
                "promoType": "percentage",
                "value": 10,
                "startAt": "2026-02-25T00:00:00Z",
                "endAt": "2026-03-03T23:59:59Z",
                "priority": 1,
            },
            {
                "id": "promo-002",
                "productId": "prd-003",
                "promoType": "fixed-amount",
                "value": 0.5,
                "startAt": "2026-02-26T00:00:00Z",
                "endAt": "2026-03-01T23:59:59Z",
                "priority": 2,
            },
        ],
    }
