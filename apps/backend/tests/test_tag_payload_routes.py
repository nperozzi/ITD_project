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


def _create_product_and_tag(client):
    product_response = client.post(
        "/api/products",
        json={"sku": "SKU-100", "name": "Coffee", "attributesJson": {}, "price": 10.0},
    )
    product_id = product_response.get_json()["id"]
    tag_response = client.post(
        "/api/tags",
        json={"status": "active", "batteryPct": 90, "productId": product_id, "shelfLocationId": None},
    )
    tag_id = tag_response.get_json()["id"]
    return product_id, tag_id


def test_publish_tag_payload_stores_and_publishes_snapshot():
    client = make_client()
    _, tag_id = _create_product_and_tag(client)

    with patch("services.tag_payload_service.publish_tag_payload") as publish_mock:
        response = client.post(f"/api/tags/{tag_id}/publish")

    data = response.get_json()

    assert response.status_code == 200
    assert data["status"] == "published"
    assert data["tagId"] == tag_id
    assert data["tagPayloadId"] == 1
    publish_mock.assert_called_once()


def test_publish_tag_payload_requires_product_assignment():
    client = make_client()
    tag_response = client.post(
        "/api/tags",
        json={"status": "active", "batteryPct": 90, "productId": None, "shelfLocationId": None},
    )
    tag_id = tag_response.get_json()["id"]

    response = client.post(f"/api/tags/{tag_id}/publish")

    assert response.status_code == 400
    assert response.get_json() == {"error": "Tag is not assigned to a product."}
