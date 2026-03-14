"""HTTP routes for browser UI and API endpoints."""

import random
from contextlib import contextmanager
from flask import Blueprint, request, jsonify, current_app
from mqtt_client import publish_price
from db.crud.crud_product import update_product
from db.crud.crud_tag import update_tag
from services.product_service import (
    ProductValidationError,
    create_product_from_payload,
    delete_product_by_id,
    get_product_details,
    list_all_products,
    update_product_from_payload,
)

# Blueprint keeps route registration organized.
api = Blueprint("api", __name__)


@contextmanager
def _session_scope():
    db = current_app.config.get("db")
    if db is None:
        raise RuntimeError("Database is not configured for this app.")

    with db.SessionLocal() as session:
        yield session


def _dashboard_data() -> dict[str, list[dict[str, object]]]:
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
        "products": [
            {
                "id": "prd-001",
                "sku": "CF-AR-1KG",
                "name": "Arabica Coffee Beans",
                "attributesJson": {"roast": "medium", "origin": "Colombia", "organic": True},
                "price": 22.9,
            },
            {
                "id": "prd-002",
                "sku": "ML-OT-1L",
                "name": "Organic Oat Milk",
                "attributesJson": {"dairyFree": True, "volumeMl": 1000},
                "price": 4.5,
            },
            {
                "id": "prd-003",
                "sku": "CH-DK-90G",
                "name": "Dark Chocolate Bar",
                "attributesJson": {"cocoaPct": 75, "vegan": True},
                "price": 3.2,
            },
        ],
        "tags": [
            {
                "id": "tag-001",
                "batteryPct": 88,
                "status": "active",
                "productId": "prd-001",
                "shelfLocationId": "sl-001",
            },
            {
                "id": "tag-002",
                "batteryPct": 24,
                "status": "low-battery",
                "productId": "prd-002",
                "shelfLocationId": "sl-002",
            },
            {
                "id": "tag-003",
                "batteryPct": 0,
                "status": "offline",
                "productId": "prd-003",
                "shelfLocationId": "sl-003",
            },
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

@api.route("/")
def index():
    # Basic health payload for the backend service.
    return jsonify({"service": "backend", "status": "ok"})

@api.route("/set_price", methods=["POST"])
def set_price():
    # Receive new price from form submission.
    price = request.form["price"]

    # Persist current product price.
    db = current_app.config.get('db')
    if db:
        with db.SessionLocal() as session:
            update_product(session, 1, price=float(price))

    # Broadcast price update through MQTT.
    publish_price(price)
    return "OK"

@api.route("/battery")
def battery():
    # Generate battery on backend so frontend relies entirely on backend value.
    battery = random.randint(1, 100)

    # Persist the generated value so other backend paths can read the latest state.
    db = current_app.config.get('db')
    if db:
        with db.SessionLocal() as session:
            update_tag(session, 1, product_id=1, battery_pct=battery)

    return jsonify({"battery": battery})


@api.route("/api/stores")
def stores():
    return jsonify(_dashboard_data()["stores"])


@api.route("/api/gateways")
def gateways():
    return jsonify(_dashboard_data()["gateways"])


@api.route("/api/shelf-locations")
def shelf_locations():
    return jsonify(_dashboard_data()["shelfLocations"])


@api.route("/api/products")
def get_all_products_route():
    with _session_scope() as session:
        return jsonify(list_all_products(session))


@api.route("/api/products/<int:product_id>")
def get_product_route(product_id: int):
    with _session_scope() as session:
        product = get_product_details(session, product_id)

    if product is None:
        return jsonify({"error": "Product not found."}), 404

    return jsonify(product)


@api.route("/api/products", methods=["POST"])
def create_product_route():
    payload = request.get_json(silent=True)
    try:
        with _session_scope() as session:
            product = create_product_from_payload(session, payload or {})
    except ProductValidationError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(product), 201


@api.route("/api/products/<int:product_id>", methods=["PATCH"])
def update_product_route(product_id: int):
    payload = request.get_json(silent=True)
    try:
        with _session_scope() as session:
            product = update_product_from_payload(session, product_id, payload or {})
    except ProductValidationError as exc:
        return jsonify({"error": str(exc)}), 400

    if product is None:
        return jsonify({"error": "Product not found."}), 404

    return jsonify(product)


@api.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product_route(product_id: int):
    with _session_scope() as session:
        is_deleted = delete_product_by_id(session, product_id)

    if not is_deleted:
        return jsonify({"error": "Product not found."}), 404

    return jsonify({"status": "deleted", "id": product_id})


@api.route("/api/tags")
def tags():
    return jsonify(_dashboard_data()["tags"])


@api.route("/api/tag-payloads")
def tag_payloads():
    return jsonify(_dashboard_data()["tagPayloads"])


@api.route("/api/promotions")
def promotions():
    return jsonify(_dashboard_data()["promotions"])
