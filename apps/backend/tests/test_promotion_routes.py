from __future__ import annotations

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


def test_get_promotions_returns_database_rows():
    client = make_client()
    product_response = client.post(
        "/api/products",
        json={"sku": "SKU-100", "name": "Coffee", "attributesJson": {}, "price": 9.5},
    )
    product_id = product_response.get_json()["id"]

    create_response = client.post(
        "/api/promotions",
        json={
            "productId": product_id,
            "promoType": "percentage",
            "value": 15,
            "startAt": "2026-03-01T00:00:00Z",
            "endAt": "2026-03-10T00:00:00Z",
            "priority": 1,
        },
    )
    assert create_response.status_code == 201

    response = client.get("/api/promotions")

    assert response.status_code == 200
    assert response.get_json() == [
        {
            "id": 1,
            "productId": product_id,
            "promoType": "percentage",
            "value": 15,
            "startAt": "2026-03-01T00:00:00Z",
            "endAt": "2026-03-10T00:00:00Z",
            "priority": 1,
        }
    ]


def test_get_single_promotion_returns_404_when_missing():
    client = make_client()

    response = client.get("/api/promotions/999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Promotion not found."}


def test_create_promotion_validates_payload():
    client = make_client()

    response = client.post(
        "/api/promotions",
        json={
            "productId": None,
            "promoType": "fixed-amount",
            "value": 10,
            "startAt": "2026-03-01T00:00:00Z",
            "endAt": "2026-03-10T00:00:00Z",
        },
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Field 'promoType' currently supports only: percentage."
    }


def test_patch_promotion_updates_existing_row():
    client = make_client()
    create_response = client.post(
        "/api/promotions",
        json={
            "productId": None,
            "promoType": "percentage",
            "value": 10,
            "startAt": "2026-03-01T00:00:00Z",
            "endAt": "2026-03-10T00:00:00Z",
            "priority": 1,
        },
    )
    promotion_id = create_response.get_json()["id"]

    response = client.patch(
        f"/api/promotions/{promotion_id}",
        json={"value": 25, "endAt": "2026-03-12T00:00:00Z"},
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "id": promotion_id,
        "productId": None,
        "promoType": "percentage",
        "value": 25,
        "startAt": "2026-03-01T00:00:00Z",
        "endAt": "2026-03-12T00:00:00Z",
        "priority": 1,
    }


def test_delete_promotion_removes_existing_row():
    client = make_client()
    create_response = client.post(
        "/api/promotions",
        json={
            "productId": None,
            "promoType": "percentage",
            "value": 5,
            "startAt": "2026-03-01T00:00:00Z",
            "endAt": "2026-03-10T00:00:00Z",
            "priority": 1,
        },
    )
    promotion_id = create_response.get_json()["id"]

    delete_response = client.delete(f"/api/promotions/{promotion_id}")
    get_response = client.get(f"/api/promotions/{promotion_id}")

    assert delete_response.status_code == 200
    assert delete_response.get_json() == {"status": "deleted", "id": promotion_id}
    assert get_response.status_code == 404
