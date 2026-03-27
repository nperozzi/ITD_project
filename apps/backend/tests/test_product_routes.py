from __future__ import annotations

from unittest.mock import patch

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.base import Base
from db.models.shelfLocation import ShelfLocation  # noqa: F401
from db.models.tag import Tag  # noqa: F401
from routes import api


class DummyDB:
    def __init__(self) -> None:
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        self.SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def make_client():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["db"] = DummyDB()
    app.register_blueprint(api)
    return app.test_client()


def test_get_products_returns_database_rows():
    client = make_client()

    create_response = client.post(
        "/api/products",
        json={
            "sku": "SKU-100",
            "name": "Coffee Beans",
            "attributesJson": {"origin": "Kenya"},
            "price": 18.5,
        },
    )
    assert create_response.status_code == 201

    response = client.get("/api/products")

    assert response.status_code == 200
    assert response.get_json() == [
        {
            "id": 1,
            "sku": "SKU-100",
            "name": "Coffee Beans",
            "attributesJson": {"origin": "Kenya"},
            "price": 18.5,
        }
    ]


def test_get_single_product_returns_404_when_missing():
    client = make_client()

    response = client.get("/api/products/999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Product not found."}


def test_create_product_validates_payload():
    client = make_client()

    response = client.post(
        "/api/products",
        json={"sku": "", "name": "Bad Product", "attributesJson": {}, "price": -1},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Field 'sku' must be a non-empty string."}


def test_patch_product_updates_existing_row():
    client = make_client()
    create_response = client.post(
        "/api/products",
        json={
            "sku": "SKU-101",
            "name": "Old Name",
            "attributesJson": {"size": "M"},
            "price": 3.2,
        },
    )
    product_id = create_response.get_json()["id"]

    response = client.patch(
        f"/api/products/{product_id}",
        json={"name": "New Name", "price": 4.0},
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "id": product_id,
        "sku": "SKU-101",
        "name": "New Name",
        "attributesJson": {"size": "M"},
        "price": 4.0,
    }


def test_patch_product_publishes_payloads_for_assigned_tags():
    client = make_client()
    product_response = client.post(
        "/api/products",
        json={
            "sku": "SKU-200",
            "name": "Coffee Beans",
            "attributesJson": {"origin": "Kenya"},
            "price": 18.5,
        },
    )
    product_id = product_response.get_json()["id"]
    tag_response = client.post(
        "/api/tags",
        json={"status": "active", "batteryPct": 90, "productId": product_id, "shelfLocationId": None},
    )
    tag_id = tag_response.get_json()["id"]

    with patch("services.tag_payload_service.publish_tag_payload") as publish_mock:
        response = client.patch(
            f"/api/products/{product_id}",
            json={"price": 19.0},
        )

    assert response.status_code == 200
    publish_mock.assert_called_once()
    assert publish_mock.call_args.args[0] == tag_id
    published_payload = publish_mock.call_args.args[1]
    assert published_payload["tagId"] == tag_id
    assert published_payload["title"] == "Coffee Beans"
    assert published_payload["finalPrice"] == 19.0


def test_delete_product_removes_existing_row():
    client = make_client()
    create_response = client.post(
        "/api/products",
        json={
            "sku": "SKU-102",
            "name": "To Delete",
            "attributesJson": {},
            "price": 6.5,
        },
    )
    product_id = create_response.get_json()["id"]

    delete_response = client.delete(f"/api/products/{product_id}")
    get_response = client.get(f"/api/products/{product_id}")

    assert delete_response.status_code == 200
    assert delete_response.get_json() == {"status": "deleted", "id": product_id}
    assert get_response.status_code == 404
