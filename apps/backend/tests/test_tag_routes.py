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


def test_get_tags_returns_database_rows_with_frontend_statuses():
    client = make_client()

    create_response = client.post(
        "/api/tags",
        json={"status": "active", "batteryPct": 20, "productId": None, "shelfLocationId": None},
    )
    assert create_response.status_code == 201

    response = client.get("/api/tags")

    assert response.status_code == 200
    assert response.get_json() == [
        {
            "id": 1,
            "batteryPct": 20,
            "status": "low-battery",
            "productId": None,
            "shelfLocationId": None,
        }
    ]


def test_get_single_tag_returns_404_when_missing():
    client = make_client()

    response = client.get("/api/tags/999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Tag not found."}


def test_create_tag_validates_payload():
    client = make_client()

    response = client.post("/api/tags", json={"status": "sleeping", "batteryPct": 50})

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Field 'status' must be one of: active, low-battery, offline, disabled."
    }


def test_patch_tag_updates_existing_row():
    client = make_client()
    create_response = client.post(
        "/api/tags",
        json={"status": "active", "batteryPct": 90, "productId": None, "shelfLocationId": None},
    )
    tag_id = create_response.get_json()["id"]

    response = client.patch(
        f"/api/tags/{tag_id}",
        json={"status": "offline", "batteryPct": 10},
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "id": tag_id,
        "batteryPct": 10,
        "status": "offline",
        "productId": None,
        "shelfLocationId": None,
    }


def test_create_tag_with_product_assignment_publishes_payload():
    client = make_client()
    product_response = client.post(
        "/api/products",
        json={"sku": "SKU-100", "name": "Coffee", "attributesJson": {}, "price": 10.0},
    )
    product_id = product_response.get_json()["id"]

    with patch("services.tag_service.publish_payload_for_tag") as publish_mock:
        response = client.post(
            "/api/tags",
            json={"status": "active", "batteryPct": 90, "productId": product_id, "shelfLocationId": None},
        )

    assert response.status_code == 201
    publish_mock.assert_called_once()
    assert publish_mock.call_args.args[1] == response.get_json()["id"]


def test_patch_tag_product_assignment_publishes_payload():
    client = make_client()
    product_response = client.post(
        "/api/products",
        json={"sku": "SKU-101", "name": "Tea", "attributesJson": {}, "price": 7.5},
    )
    product_id = product_response.get_json()["id"]
    tag_response = client.post(
        "/api/tags",
        json={"status": "active", "batteryPct": 90, "productId": None, "shelfLocationId": None},
    )
    tag_id = tag_response.get_json()["id"]

    with patch("services.tag_service.publish_payload_for_tag") as publish_mock:
        response = client.patch(
            f"/api/tags/{tag_id}",
            json={"productId": product_id},
        )

    assert response.status_code == 200
    publish_mock.assert_called_once()
    assert publish_mock.call_args.args[1] == tag_id


def test_patch_tag_without_assignment_change_does_not_publish_payload():
    client = make_client()
    tag_response = client.post(
        "/api/tags",
        json={"status": "active", "batteryPct": 90, "productId": None, "shelfLocationId": None},
    )
    tag_id = tag_response.get_json()["id"]

    with patch("services.tag_service.publish_payload_for_tag") as publish_mock:
        response = client.patch(
            f"/api/tags/{tag_id}",
            json={"batteryPct": 10},
        )

    assert response.status_code == 200
    publish_mock.assert_not_called()


def test_delete_tag_removes_existing_row():
    client = make_client()
    create_response = client.post(
        "/api/tags",
        json={"status": "active", "batteryPct": 50, "productId": None, "shelfLocationId": None},
    )
    tag_id = create_response.get_json()["id"]

    delete_response = client.delete(f"/api/tags/{tag_id}")
    get_response = client.get(f"/api/tags/{tag_id}")

    assert delete_response.status_code == 200
    assert delete_response.get_json() == {"status": "deleted", "id": tag_id}
    assert get_response.status_code == 404
